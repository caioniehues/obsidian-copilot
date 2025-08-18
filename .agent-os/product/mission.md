# Product Mission

> Last Updated: 2025-08-18
> Version: 1.0.0

## Pitch

Transform Obsidian into the ultimate knowledge synthesis companion by creating the first RAG system exclusively optimized for Claude's 200K context window. Enable researchers, writers, and knowledge workers to leverage their entire vault as intelligent context for deep analytical work, turning personal knowledge bases into AI-powered research assistants.

## Users

**Primary Users:**
- Academic researchers managing extensive literature collections
- Knowledge workers with complex, interconnected note systems
- Writers conducting research across multiple sources and domains
- Consultants synthesizing information from diverse client materials

**User Characteristics:**
- Heavy Obsidian users with 500+ notes
- Regular Claude users familiar with advanced prompting
- Value deep analysis over quick answers
- Prioritize data privacy and local processing

## The Problem

Current RAG implementations for Obsidian are limited by small context windows (4K-8K tokens), forcing them to:
- Return only small, fragmented chunks of information
- Miss complex relationships between distant concepts
- Require multiple queries for comprehensive analysis
- Lose nuanced context that spans multiple documents

Knowledge workers end up manually copy-pasting multiple notes into Claude, losing time and breaking their workflow. They need a system that can intelligently select and synthesize their entire knowledge base within Claude's massive context capacity.

## Differentiators

**Claude-First Architecture:**
- Built exclusively for Claude's 200K context window
- Intelligent context packing strategies that maximize token utilization
- Multi-document synthesis capabilities impossible with smaller contexts

**Vault-Wide Intelligence:**
- Analyzes entire knowledge graphs, not just individual documents
- Understands complex concept relationships across the full vault
- Provides comprehensive insights that span multiple note hierarchies

**Privacy-Focused Local Processing:**
- All indexing and retrieval happens locally
- No external API calls for document processing
- Complete control over sensitive research and business information

**Advanced Context Strategies:**
- Smart document prioritization based on relevance and relationships
- Hierarchical context building from most to least relevant
- Dynamic context adjustment based on query complexity

## Key Features

**Core Retrieval Engine:**
- Hybrid search combining semantic similarity and graph relationships
- Intelligent document chunking that preserves context boundaries
- Multi-level relevance scoring incorporating link structures

**Claude Integration:**
- Seamless Claude Code CLI integration
- Optimized prompt templates for different analysis types
- Context streaming for real-time synthesis

**Advanced Analysis Modes:**
- Cross-vault concept mapping
- Multi-document comparative analysis
- Timeline-based synthesis for historical research
- Argument chain reconstruction from distributed evidence

**Local-First Architecture:**
- Docker-containerized backend for easy deployment
- No cloud dependencies for core functionality
- Encrypted local storage for sensitive materials

**Obsidian Native Experience:**
- Invisible integration with existing workflows
- Results displayed in native Obsidian format with proper linking
- Maintains vault integrity and existing organization systems