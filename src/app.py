"""
Claude-optimized FastAPI app for retrieval-augmented generation.
Leverages Claude's 200K context window for advanced document synthesis and analysis.
"""

import asyncio
import json
import os
import pickle
import subprocess
import tempfile
import time
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import AutoModel, AutoTokenizer

from src.logger import logger
from src.prep.build_opensearch_index import INDEX_NAME, get_opensearch, query_opensearch
from src.prep.build_semantic_index import query_semantic
from src.agents_enhanced import enhanced_agent_manager, ParallelTask
from src.services import service_manager
from src.exceptions import (
    CopilotError, 
    ServiceUnavailableError, 
    FileNotFoundError,
    TimeoutError,
    APIClientError
)
from src.utils.retry import timeout_wrapper, api_retry

# Services will be initialized on startup
vault = None
os_client = None
doc_embeddings_array = None
embedding_index = None
tokenizer = None
model = None


# Create app
app = FastAPI(
    title="Obsidian Copilot API",
    description="Claude-optimized retrieval-augmented generation for Obsidian",
    version="1.0.0"
)

# List of allowed origins. You can also allow all by using ["*"]
origins = [
    "app://obsidian.md",  # Allow obsidian app
    "http://localhost",  # or whatever hosts you want to allow
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize all services on application startup."""
    global vault, os_client, doc_embeddings_array, embedding_index, tokenizer, model
    
    try:
        logger.info("Starting Obsidian Copilot API...")
        
        # Initialize all services with robust error handling
        service_status = await service_manager.initialize_all_services()
        
        # Get services for global access (backward compatibility)
        vault = service_manager.get_service('vault')
        os_client = service_manager.get_service('opensearch_client')
        doc_embeddings_array = service_manager.get_service('doc_embeddings_array')
        embedding_index = service_manager.get_service('embedding_index')
        tokenizer = service_manager.get_service('tokenizer')
        model = service_manager.get_service('model')
        
        logger.info("✓ Obsidian Copilot API started successfully")
        logger.info(f"Service status: {service_status}")
        
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown all services."""
    logger.info("Shutting down Obsidian Copilot API...")
    
    try:
        await service_manager.shutdown()
        logger.info("✓ Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    try:
        health_status = service_manager.get_health_status()
        
        # Determine overall health
        is_healthy = (
            health_status["initialized"] and
            health_status["services"]["vault_data"] and
            (health_status["services"]["opensearch"] or health_status["services"]["semantic_index"])
        )
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": health_status["services"],
            "degraded_services": health_status["degraded_services"]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        )


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service status and metrics."""
    try:
        health_status = service_manager.get_health_status()
        
        # Add additional metrics
        metrics = {}
        
        if vault:
            metrics["vault_documents"] = len(vault)
        
        if doc_embeddings_array is not None:
            metrics["embedding_dimensions"] = doc_embeddings_array.shape
        
        return {
            "status": "healthy" if health_status["initialized"] else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "dependencies": health_status,
            "metrics": metrics,
            "agents": {
                "available": True,  # TODO: Get from agent manager
                "count": 0  # TODO: Get actual count
            }
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Detailed health check failed: {str(e)}"
        )


class ContextStrategy(str, Enum):
    """Context building strategies optimized for Claude's 200K window."""
    FULL_DOCS = "full_docs"  # Send complete documents
    SMART_CHUNKS = "smart_chunks"  # Intelligent chunking based on structure
    HIERARCHICAL = "hierarchical"  # Summaries + relevant sections


class GenerationRequest(BaseModel):
    """Claude-optimized generation request."""
    query: str
    context_strategy: ContextStrategy = ContextStrategy.SMART_CHUNKS
    system_prompt: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    model: str = "claude-3-5-sonnet-20241022"
    include_full_docs: bool = False  # Whether to include complete documents
    max_context_tokens: int = 100000  # Default to 100K, can go up to 200K


class GenerationResponse(BaseModel):
    """Claude generation response."""
    response: str
    context_used: str  # Description of context strategy used
    tokens_used: int  # Estimated tokens in context
    model: str
    generation_time: Optional[float] = None


class VaultAnalysisRequest(BaseModel):
    """Request for vault-wide analysis."""
    topic: str
    depth: int = 3  # How many levels deep to analyze
    max_documents: int = 50  # Maximum documents to include
    

class SynthesisRequest(BaseModel):
    """Request for multi-document synthesis."""
    note_paths: List[str]  # Full paths to notes to synthesize
    synthesis_type: str = "summary"  # summary, outline, connections
    

class ProgressiveDraftRequest(BaseModel):
    """Request for progressive document generation."""
    outline: Dict[str, List[str]]  # Section headers and bullet points
    style: str = "academic"  # academic, casual, technical


# Agent-related models
class AgentExecuteRequest(BaseModel):
    """Request to execute one or more agents."""
    agent_names: List[str]  # Names of agents to execute
    context: Optional[Dict[str, Any]] = {}  # Context for agent execution
    parallel: bool = True  # Execute agents in parallel
    timeout: Optional[int] = 60  # Timeout in seconds

class AgentStatusRequest(BaseModel):
    """Request for agent status information."""
    agent_names: Optional[List[str]] = None  # Specific agents, or all if None

class AgentResponse(BaseModel):
    """Response from agent execution."""
    agent_name: str
    status: str  # "success", "error", "timeout"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: str

class AgentListResponse(BaseModel):
    """Response listing available agents."""
    agents: List[Dict[str, Any]]
    total_count: int
    enabled_count: int


def parse_os_response(response: dict) -> List[dict]:
    """
    Parse response from opensearch index.

    Args:
        response: Response from opensearch query.

    Returns:
        List of hits with chunkID and rank
    """
    hits = []

    for rank, hit in enumerate(response["hits"]["hits"]):
        hits.append({"id": hit["_id"], "rank": rank})

    return hits


def parse_semantic_response(
    indices: np.ndarray, embedding_index: Dict[int, str]
) -> List[dict]:
    """
    Parse response from semantic index.

    Args:
        indices: Response from semantic query, an array of ints.

    Returns:
        List of hits with chunkID and rank
    """
    hits = []

    for rank, idx in enumerate(indices):
        hits.append({"id": embedding_index[idx], "rank": rank})

    return hits


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for Claude. 
    Claude uses roughly 1 token per 4 characters as a conservative estimate.
    
    Args:
        text: String to estimate tokens for
    
    Returns:
        Estimated number of tokens
    """
    # Conservative estimate: ~4 characters per token
    return len(text) // 4


def get_context_for_claude(
    hits: List[dict], 
    strategy: ContextStrategy = ContextStrategy.SMART_CHUNKS,
    max_tokens: int = 100000,
    include_full_docs: bool = False
) -> Dict[str, any]:
    """
    Build context optimized for Claude's large context window.

    Args:
        hits: List of hits from opensearch, semantic index, etc.
        strategy: Context building strategy
        max_tokens: Maximum tokens to allow. Defaults to 100K.
        include_full_docs: Whether to include complete documents

    Returns:
        Dict containing context and metadata
    """
    # Combine and rank hits
    df = pd.DataFrame(hits)
    df["score"] = df["rank"].apply(lambda x: 10 - x)
    ranked = (
        df.groupby("id")
        .agg({"score": "sum"})
        .sort_values("score", ascending=False)
        .reset_index()
    )

    context_parts = []
    token_count = 0
    docs_included = []
    
    if strategy == ContextStrategy.FULL_DOCS or include_full_docs:
        # Group chunks by document and include full documents
        doc_groups = {}
        for id in ranked["id"].tolist():
            doc_title = vault[id]["title"]
            if doc_title not in doc_groups:
                doc_groups[doc_title] = []
            doc_groups[doc_title].append(vault[id]["chunk"])
        
        for title, chunks in doc_groups.items():
            full_doc = "\n\n".join(chunks)
            doc_tokens = estimate_tokens(full_doc)
            
            if token_count + doc_tokens <= max_tokens:
                context_parts.append({
                    "title": title,
                    "content": full_doc,
                    "type": "full_document"
                })
                token_count += doc_tokens
                docs_included.append(title)
            else:
                break
                
    elif strategy == ContextStrategy.HIERARCHICAL:
        # Include summaries first, then detailed sections
        # TODO: Implement hierarchical context building
        pass
        
    else:  # SMART_CHUNKS (default)
        for id in ranked["id"].tolist():
            chunk = vault[id]["chunk"]
            title = vault[id]["title"]
            chunk_tokens = estimate_tokens(chunk)
            
            if token_count + chunk_tokens <= max_tokens:
                context_parts.append({
                    "title": title,
                    "content": chunk,
                    "type": "chunk"
                })
                token_count += chunk_tokens
                if title not in docs_included:
                    docs_included.append(title)
            else:
                break
    
    return {
        "context": context_parts,
        "tokens_used": token_count,
        "documents_included": docs_included,
        "strategy_used": strategy.value
    }


@app.post("/generate", response_model=GenerationResponse)
async def generate_with_claude(request: GenerationRequest):
    """
    Generate text using Claude Code CLI with optimized context strategies.
    Leverages Claude's 200K context window for comprehensive understanding.
    """
    import time
    start_time = time.time()
    
    try:
        # Get relevant documents first
        os_response = query_opensearch(request.query, os_client, INDEX_NAME)
        os_hits = parse_os_response(os_response)
        
        semantic_response = query_semantic(request.query, tokenizer, model, doc_embeddings_array)
        semantic_hits = parse_semantic_response(semantic_response, embedding_index)
        
        # Build optimized context for Claude
        context_data = get_context_for_claude(
            os_hits + semantic_hits,
            strategy=request.context_strategy,
            max_tokens=request.max_context_tokens,
            include_full_docs=request.include_full_docs
        )
        
        # Format context based on type
        context_parts = []
        for item in context_data["context"]:
            if item["type"] == "full_document":
                context_parts.append(
                    f"=== FULL DOCUMENT: {item['title']} ===\n"
                    f"{item['content']}\n"
                    f"=== END DOCUMENT ===\n"
                )
            else:
                context_parts.append(
                    f"Source: {item['title']}\n"
                    f"Content: {item['content']}\n"
                    f"---"
                )
        context = "\n".join(context_parts)
        
        # Prepare the full prompt
        full_prompt = f"""{request.system_prompt}

Retrieved Context:
{context}

User Query: {request.query}

Please generate a comprehensive response based on the above context. When referencing information from the context, include markdown references to the source documents."""
        
        # Option 1: Direct CLI invocation with stdin
        try:
            # First try using claude command directly
            result = subprocess.run(
                [
                    "claude", 
                    "--model", request.model,
                    "--max-tokens", str(request.max_tokens or 4000)
                ],
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode != 0:
                # If claude command fails, try with full path if available
                claude_path = os.environ.get("CLAUDE_CODE_PATH", "/usr/local/bin/claude")
                if os.path.exists(claude_path):
                    result = subprocess.run(
                        [
                            claude_path,
                            "--model", request.model,
                            "--max-tokens", str(request.max_tokens or 4000)
                        ],
                        input=full_prompt,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                
                if result.returncode != 0:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Claude Code error: {result.stderr}"
                    )
            
            generation_time = time.time() - start_time
            
            return GenerationResponse(
                response=result.stdout.strip(),
                context_used=f"{context_data['strategy_used']} with {len(context_data['documents_included'])} documents",
                tokens_used=context_data["tokens_used"],
                model=request.model,
                generation_time=generation_time
            )
            
        except FileNotFoundError:
            # Option 2: Using a context file (better for large contexts)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(f"# Context\n\n{context}")
                context_file = f.name
            
            try:
                # Try using context file approach
                prompt_with_query = f"{request.system_prompt}\n\nQuery: {request.query}"
                
                result_with_file = subprocess.run(
                    [
                        os.environ.get("CLAUDE_CODE_PATH", "claude"),
                        "--context", context_file,
                        "--model", request.model,
                        "--max-tokens", str(request.max_tokens or 4000)
                    ],
                    input=prompt_with_query,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result_with_file.returncode != 0:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Claude Code not found or error: {result_with_file.stderr}"
                    )
                
                generation_time = time.time() - start_time
                
                return GenerationResponse(
                    response=result_with_file.stdout.strip(),
                    context_used=f"{context_data['strategy_used']} with {len(context_data['documents_included'])} documents",
                    tokens_used=context_data["tokens_used"],
                    model=request.model,
                    generation_time=generation_time
                )
                
            finally:
                os.unlink(context_file)  # Clean up temp file
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Generation timeout after 60 seconds")
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_streaming")
async def generate_streaming(request: GenerationRequest):
    """
    Simulate streaming by chunking the response.
    Since Claude Code CLI doesn't support streaming, we generate the full response
    and then stream it in chunks for better UX.
    """
    # Generate full response first
    full_response = await generate_with_claude(request)
    
    # Simulate streaming by yielding chunks
    async def generate():
        words = full_response.response.split()
        chunk_size = 5  # Send 5 words at a time
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            if i + chunk_size < len(words):
                chunk += " "  # Add space if not last chunk
            
            # Format as Server-Sent Events
            yield f"data: {json.dumps({'content': chunk})}\n\n"
            await asyncio.sleep(0.05)  # Small delay to simulate streaming
        
        # Send completion signal
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/analyze_vault")
async def analyze_vault(request: VaultAnalysisRequest):
    """
    Perform vault-wide analysis on a topic using Claude's 200K context.
    This can analyze relationships across 50+ documents simultaneously.
    """
    import time
    start_time = time.time()
    
    # Search for all relevant documents
    os_response = query_opensearch(request.topic, os_client, INDEX_NAME, size=request.max_documents)
    os_hits = parse_os_response(os_response)
    
    semantic_response = query_semantic(request.topic, tokenizer, model, doc_embeddings_array, k=request.max_documents)
    semantic_hits = parse_semantic_response(semantic_response, embedding_index)
    
    # Get full documents for comprehensive analysis
    context_data = get_context_for_claude(
        os_hits + semantic_hits,
        strategy=ContextStrategy.FULL_DOCS,
        max_tokens=150000  # Use more tokens for vault analysis
    )
    
    # Create analysis prompt
    analysis_prompt = f"""You are analyzing a knowledge vault on the topic: {request.topic}

I'm providing you with {len(context_data['documents_included'])} complete documents from the vault.
Please provide a comprehensive analysis that includes:

1. **Main Themes**: Identify the primary themes and concepts across all documents
2. **Connections**: Map relationships and connections between different documents and ideas
3. **Patterns**: Identify recurring patterns, methodologies, or approaches
4. **Gaps**: Note any gaps in knowledge or areas that need more exploration
5. **Synthesis**: Provide a high-level synthesis of the collective knowledge

Depth level requested: {request.depth}/5 (1=overview, 5=exhaustive detail)

Documents included in this analysis:
{', '.join(context_data['documents_included'])}

===== VAULT CONTENT =====
"""
    
    # Add all documents to context
    for item in context_data["context"]:
        analysis_prompt += f"\n\n=== {item['title']} ===\n{item['content']}\n"
    
    analysis_prompt += "\n\n===== END VAULT CONTENT =====\n\nProvide your comprehensive analysis:"
    
    # Call Claude for analysis
    try:
        result = subprocess.run(
            [
                os.environ.get("CLAUDE_CODE_PATH", "claude"),
                "--model", "claude-3-5-sonnet-20241022",
                "--max-tokens", "8000"
            ],
            input=analysis_prompt,
            capture_output=True,
            text=True,
            timeout=120  # Longer timeout for analysis
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Claude analysis failed: {result.stderr}")
        
        generation_time = time.time() - start_time
        
        return {
            "analysis": result.stdout.strip(),
            "documents_analyzed": len(context_data['documents_included']),
            "tokens_used": context_data["tokens_used"],
            "generation_time": generation_time,
            "documents": context_data['documents_included']
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Analysis timeout after 120 seconds")
    except Exception as e:
        logger.error(f"Vault analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/synthesize_notes")
async def synthesize_notes(request: SynthesisRequest):
    """
    Create a synthesis from multiple complete notes.
    Leverages Claude to create summaries, outlines, or connection maps.
    """
    import time
    start_time = time.time()
    
    # Load requested notes
    notes_content = []
    total_tokens = 0
    
    for note_path in request.note_paths:
        # Find the note in vault
        matching_docs = [v for k, v in vault.items() if v.get("title") == note_path]
        if matching_docs:
            # Combine all chunks of the document
            doc_chunks = [doc["chunk"] for doc in matching_docs]
            full_content = "\n\n".join(doc_chunks)
            notes_content.append({
                "title": note_path,
                "content": full_content
            })
            total_tokens += estimate_tokens(full_content)
    
    if not notes_content:
        raise HTTPException(status_code=404, detail="No matching notes found")
    
    # Create synthesis prompt based on type
    if request.synthesis_type == "summary":
        synthesis_prompt = "Create a comprehensive summary that captures the key points from all these notes:"
    elif request.synthesis_type == "outline":
        synthesis_prompt = "Create a detailed outline that organizes the information from all these notes:"
    elif request.synthesis_type == "connections":
        synthesis_prompt = "Map the connections and relationships between ideas across these notes:"
    else:
        synthesis_prompt = "Synthesize the information from these notes:"
    
    full_prompt = f"""You are creating a {request.synthesis_type} from {len(notes_content)} notes.

{synthesis_prompt}

===== NOTES CONTENT =====
"""
    
    for note in notes_content:
        full_prompt += f"\n\n=== {note['title']} ===\n{note['content']}\n"
    
    full_prompt += f"\n\n===== END NOTES =====\n\nProvide your {request.synthesis_type}:"
    
    # Call Claude
    try:
        result = subprocess.run(
            [
                os.environ.get("CLAUDE_CODE_PATH", "claude"),
                "--model", "claude-3-5-sonnet-20241022",
                "--max-tokens", "6000"
            ],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=90
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Claude synthesis failed: {result.stderr}")
        
        generation_time = time.time() - start_time
        
        return {
            "synthesis": result.stdout.strip(),
            "type": request.synthesis_type,
            "notes_synthesized": len(notes_content),
            "tokens_used": total_tokens,
            "generation_time": generation_time
        }
        
    except Exception as e:
        logger.error(f"Synthesis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_context")
def get_context(
    query: str, 
    strategy: str = "smart_chunks",
    max_tokens: int = 100000
):
    """
    Get optimized context for Claude based on query.
    Returns structured context with metadata.
    """
    if not query:
        raise ValueError(
            f"Query is empty: {query}. Did you try to draft using an empty selection?"
        )
    
    # Get hits from opensearch
    os_response = query_opensearch(query, os_client, INDEX_NAME)
    os_hits = parse_os_response(os_response)
    logger.debug(f"OS hits: {os_hits}")

    # Get hits from semantic index
    semantic_response = query_semantic(query, tokenizer, model, doc_embeddings_array)
    semantic_hits = parse_semantic_response(semantic_response, embedding_index)
    logger.debug(f"Semantic hits: {semantic_hits}")

    # Get optimized context
    context_strategy = ContextStrategy(strategy)
    context_data = get_context_for_claude(
        os_hits + semantic_hits,
        strategy=context_strategy,
        max_tokens=max_tokens
    )
    
    # Format for plugin consumption
    return {
        "chunks": context_data["context"],
        "metadata": {
            "tokens_used": context_data["tokens_used"],
            "documents_included": context_data["documents_included"],
            "strategy": context_data["strategy_used"]
        }
    }


# Agent OS Endpoints - Parallel Execution Support

@app.on_event("startup")
async def startup_event():
    """Initialize agent manager and Redis on startup"""
    await enhanced_agent_manager.initialize_redis()
    logger.info("Agent OS initialized with parallel execution support")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup agent resources on shutdown"""
    enhanced_agent_manager.cleanup()
    logger.info("Agent OS resources cleaned up")

@app.post("/agents/execute")
async def execute_agents(request: AgentExecuteRequest):
    """
    Execute one or more agents with parallel processing support.
    Optimized for high performance through concurrent execution.
    """
    start_time = time.time()
    
    try:
        if request.parallel and len(request.agent_names) > 1:
            # Execute agents in parallel for maximum performance
            results = await enhanced_agent_manager.execute_agents_parallel(
                request.agent_names, 
                request.context
            )
            
            # Format results
            agent_responses = []
            for agent_name, result in results.items():
                if isinstance(result, dict) and 'error' in result:
                    status = "error"
                    error = result['error']
                    result_data = None
                else:
                    status = "success"
                    error = None
                    result_data = result
                
                agent_responses.append(AgentResponse(
                    agent_name=agent_name,
                    status=status,
                    result=result_data,
                    error=error,
                    execution_time=time.time() - start_time,
                    timestamp=datetime.utcnow().isoformat()
                ))
            
            return {
                "results": [resp.dict() for resp in agent_responses],
                "execution_mode": "parallel",
                "total_execution_time": time.time() - start_time,
                "agents_executed": len(request.agent_names)
            }
        
        else:
            # Sequential execution for single agent or when parallel=False
            results = []
            for agent_name in request.agent_names:
                agent_start = time.time()
                try:
                    result = await enhanced_agent_manager.execute_agent(
                        agent_name, 
                        request.context
                    )
                    
                    results.append(AgentResponse(
                        agent_name=agent_name,
                        status="success",
                        result=result,
                        execution_time=time.time() - agent_start,
                        timestamp=datetime.utcnow().isoformat()
                    ))
                    
                except Exception as e:
                    results.append(AgentResponse(
                        agent_name=agent_name,
                        status="error",
                        error=str(e),
                        execution_time=time.time() - agent_start,
                        timestamp=datetime.utcnow().isoformat()
                    ))
            
            return {
                "results": [resp.dict() for resp in results],
                "execution_mode": "sequential",
                "total_execution_time": time.time() - start_time,
                "agents_executed": len(request.agent_names)
            }
    
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/status")
async def get_agents_status(agent_names: Optional[str] = None):
    """
    Get status of agents with parallel status checking for performance.
    """
    try:
        if agent_names:
            # Parse comma-separated agent names
            names_list = [name.strip() for name in agent_names.split(',')]
            
            # Get status in parallel
            status_results = await enhanced_agent_manager.get_agent_status_parallel(names_list)
            
            return {
                "agents": [
                    {"name": name, **status} 
                    for name, status in status_results.items()
                ],
                "total_count": len(names_list),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        else:
            # Get all agent statuses
            all_agents = ['vault-analyzer', 'synthesis-assistant', 'context-optimizer', 
                         'suggestion-engine', 'research-assistant']
            
            status_results = await enhanced_agent_manager.get_agent_status_parallel(all_agents)
            
            agents_data = [
                {"name": name, **status} 
                for name, status in status_results.items()
            ]
            
            enabled_count = sum(1 for agent in agents_data if agent.get('enabled', False))
            
            return AgentListResponse(
                agents=agents_data,
                total_count=len(agents_data),
                enabled_count=enabled_count
            ).dict()
    
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/vault-analyze")
async def analyze_vault():
    """
    Trigger comprehensive vault analysis with parallel processing.
    Returns detailed analysis results in real-time.
    """
    try:
        # Execute vault analyzer with full parallel processing
        result = await enhanced_agent_manager.execute_agent(
            'vault-analyzer', 
            {'analysis_type': 'comprehensive'}
        )
        
        return {
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat(),
            "performance_optimized": True
        }
    
    except Exception as e:
        logger.error(f"Vault analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/synthesize")
async def agent_synthesize(request: SynthesisRequest):
    """
    Create synthesis using the synthesis assistant agent.
    Leverages parallel processing for multi-document analysis.
    """
    try:
        context = {
            'documents': request.note_paths,
            'synthesis_type': request.synthesis_type,
            'parallel_analysis': True
        }
        
        result = await enhanced_agent_manager.execute_agent(
            'synthesis-assistant',
            context
        )
        
        return {
            "synthesis_result": result,
            "documents_processed": len(request.note_paths),
            "synthesis_type": request.synthesis_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Agent synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/optimize-context")
async def optimize_context():
    """
    Trigger context optimization with parallel performance analysis.
    """
    try:
        result = await enhanced_agent_manager.execute_agent(
            'context-optimizer',
            {'optimization_mode': 'comprehensive'}
        )
        
        return {
            "optimization_result": result,
            "timestamp": datetime.utcnow().isoformat(),
            "performance_boost": "enabled"
        }
    
    except Exception as e:
        logger.error(f"Context optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/health")
async def agents_health_check():
    """
    Health check endpoint for agent system with parallel monitoring.
    """
    try:
        # Check all critical agents in parallel
        critical_agents = ['vault-analyzer', 'synthesis-assistant', 'context-optimizer']
        
        health_results = await enhanced_agent_manager.get_agent_status_parallel(critical_agents)
        
        all_healthy = all(
            not isinstance(result, dict) or 'error' not in result
            for result in health_results.values()
        )
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "agents": health_results,
            "parallel_execution": "enabled",
            "redis_available": enhanced_agent_manager.redis_client is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    logger.info(f"Claude-optimized Obsidian Copilot backend started")
    logger.info(f"Claude path: {os.getenv('CLAUDE_CODE_PATH', 'claude')}")
    logger.info(f"Max context tokens: {os.getenv('MAX_CONTEXT_TOKENS', '100000')}")
    
    # Test query
    test_query = "Examples of bandits in industry"
    os_response = query_opensearch(test_query, os_client, INDEX_NAME)
    os_hits = parse_os_response(os_response)
    logger.debug(f"OS hits: {os_hits}")
    
    semantic_response = query_semantic(
        f"query: {test_query}", tokenizer, model, doc_embeddings_array
    )
    semantic_hits = parse_semantic_response(semantic_response, embedding_index)
    logger.debug(f"Semantic hits: {semantic_hits}")

    # Test new context building
    context_data = get_context_for_claude(
        os_hits + semantic_hits,
        strategy=ContextStrategy.SMART_CHUNKS,
        max_tokens=100000
    )
    logger.info(f"Context built: {context_data['tokens_used']} tokens, {len(context_data['documents_included'])} documents")
