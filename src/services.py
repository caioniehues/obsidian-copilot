"""
Service management with robust error handling, health checks, and graceful degradation.
Provides centralized service initialization and dependency management.
"""

import os
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
from transformers import AutoModel, AutoTokenizer

from src.exceptions import (
    FileNotFoundError, 
    ModelLoadError, 
    OpenSearchError, 
    ConfigurationError,
    ServiceUnavailableError
)
from src.utils.retry import retry_with_backoff, CircuitBreaker, HealthChecker
from src.prep.build_opensearch_index import get_opensearch
from src.logger import logger


class ServiceManager:
    """Manages all external services and dependencies with robust error handling."""
    
    def __init__(self):
        self.services: Dict[str, Any] = {}
        self.health_checkers: Dict[str, HealthChecker] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._initialized = False
        
        # Service status tracking
        self.service_status: Dict[str, bool] = {
            'opensearch': False,
            'redis': False,
            'vault_data': False,
            'semantic_index': False,
            'ml_models': False
        }
    
    async def initialize_all_services(self) -> Dict[str, bool]:
        """
        Initialize all services with comprehensive error handling.
        
        Returns:
            Dict mapping service names to their initialization status
        """
        logger.info("Initializing all services...")
        
        # Initialize in dependency order
        initialization_order = [
            ('vault_data', self._initialize_vault_data),
            ('opensearch', self._initialize_opensearch),
            ('semantic_index', self._initialize_semantic_index),
            ('ml_models', self._initialize_ml_models),
            ('redis', self._initialize_redis)
        ]
        
        for service_name, init_func in initialization_order:
            try:
                await init_func()
                self.service_status[service_name] = True
                logger.info(f"✓ {service_name} initialized successfully")
            except Exception as e:
                logger.error(f"✗ Failed to initialize {service_name}: {e}")
                self.service_status[service_name] = False
                
                # Some services are critical, others can be degraded
                if service_name in ['vault_data']:
                    logger.critical(f"Critical service {service_name} failed. Cannot continue.")
                    raise ConfigurationError(
                        f"Critical service initialization failed: {service_name}",
                        error_code="CRITICAL_SERVICE_FAILED",
                        details={"service": service_name, "error": str(e)}
                    )
        
        self._initialized = True
        logger.info(f"Service initialization complete. Status: {self.service_status}")
        return self.service_status.copy()
    
    @retry_with_backoff(max_retries=2, base_delay=1.0)
    async def _initialize_vault_data(self):
        """Initialize vault data with error handling."""
        data_dir = Path("data")
        vault_file = data_dir / "vault_dict.pickle"
        
        if not data_dir.exists():
            raise FileNotFoundError(
                f"Data directory not found: {data_dir}",
                error_code="DATA_DIR_MISSING"
            )
        
        if not vault_file.exists():
            raise FileNotFoundError(
                f"Vault dictionary file not found: {vault_file}",
                error_code="VAULT_DICT_MISSING"
            )
        
        try:
            with open(vault_file, "rb") as f:
                vault_dict = pickle.load(f)
            
            if not vault_dict:
                raise ConfigurationError(
                    "Vault dictionary is empty",
                    error_code="EMPTY_VAULT"
                )
            
            self.services['vault'] = vault_dict
            logger.info(f"Vault loaded with {len(vault_dict)} documents")
            
        except (pickle.PickleError, EOFError) as e:
            raise FileNotFoundError(
                f"Failed to load vault dictionary: {e}",
                error_code="VAULT_DICT_CORRUPTED"
            )
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    async def _initialize_opensearch(self):
        """Initialize OpenSearch with fallback and error handling."""
        circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0,
            expected_exception=(ConnectionError, OpenSearchError)
        )
        self.circuit_breakers['opensearch'] = circuit_breaker
        
        # Try opensearch host first, then localhost
        hosts_to_try = ['opensearch', 'localhost']
        last_error = None
        
        for host in hosts_to_try:
            try:
                client = get_opensearch(host)
                
                # Test connection
                info = client.info()
                logger.info(f"OpenSearch connected to {host}: {info.get('version', {}).get('number', 'unknown')}")
                
                self.services['opensearch_client'] = client
                self.services['opensearch_host'] = host
                
                # Setup health checker
                self.health_checkers['opensearch'] = HealthChecker(circuit_breaker)
                return
                
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to connect to OpenSearch at {host}: {e}")
                continue
        
        # If we get here, all hosts failed
        raise OpenSearchError(
            f"Failed to connect to OpenSearch on any host: {last_error}",
            error_code="OPENSEARCH_CONNECTION_FAILED",
            details={"hosts_tried": hosts_to_try, "last_error": str(last_error)}
        )
    
    @retry_with_backoff(max_retries=2, base_delay=1.0)
    async def _initialize_semantic_index(self):
        """Initialize semantic search index with validation."""
        data_dir = Path("data")
        embeddings_file = data_dir / "doc_embeddings_array.npy"
        index_file = data_dir / "embedding_index.pickle"
        
        # Check if files exist
        missing_files = []
        if not embeddings_file.exists():
            missing_files.append(str(embeddings_file))
        if not index_file.exists():
            missing_files.append(str(index_file))
        
        if missing_files:
            raise FileNotFoundError(
                f"Semantic index files missing: {missing_files}",
                error_code="SEMANTIC_INDEX_MISSING",
                details={"missing_files": missing_files}
            )
        
        try:
            # Load embeddings
            embeddings = np.load(embeddings_file)
            
            # Load index
            with open(index_file, "rb") as f:
                embedding_index = pickle.load(f)
            
            # Validate data consistency
            if len(embedding_index) != embeddings.shape[0]:
                raise ConfigurationError(
                    f"Embedding index size mismatch: index={len(embedding_index)}, embeddings={embeddings.shape[0]}",
                    error_code="INDEX_SIZE_MISMATCH"
                )
            
            self.services['doc_embeddings_array'] = embeddings
            self.services['embedding_index'] = embedding_index
            
            logger.info(f"Semantic index loaded: {embeddings.shape[0]} embeddings, dimension {embeddings.shape[1]}")
            
        except (np.core.exceptions.MemoryError, OSError) as e:
            raise FileNotFoundError(
                f"Failed to load semantic index files: {e}",
                error_code="SEMANTIC_INDEX_LOAD_FAILED"
            )
        except (pickle.PickleError, EOFError) as e:
            raise FileNotFoundError(
                f"Failed to load embedding index: {e}",
                error_code="EMBEDDING_INDEX_CORRUPTED"
            )
    
    @retry_with_backoff(max_retries=2, base_delay=3.0)
    async def _initialize_ml_models(self):
        """Initialize ML models with error handling."""
        model_name = "intfloat/e5-small-v2"
        
        try:
            # Set environment variable to avoid parallelism issues
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Load model
            model = AutoModel.from_pretrained(model_name)
            
            # Validate model is working
            test_input = tokenizer("test", return_tensors="pt")
            _ = model(**test_input)
            
            self.services['tokenizer'] = tokenizer
            self.services['model'] = model
            
            logger.info(f"ML models loaded successfully: {model_name}")
            
        except Exception as e:
            raise ModelLoadError(
                f"Failed to load ML models: {e}",
                error_code="MODEL_LOAD_FAILED",
                details={"model_name": model_name, "error": str(e)}
            )
    
    async def _initialize_redis(self):
        """Initialize Redis with graceful degradation."""
        try:
            import redis.asyncio as redis
            
            client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await client.ping()
            
            self.services['redis_client'] = client
            logger.info("Redis initialized successfully")
            
        except Exception as e:
            logger.warning(f"Redis initialization failed (will use in-memory cache): {e}")
            # Redis is optional - use None to indicate fallback to in-memory
            self.services['redis_client'] = None
    
    def get_service(self, service_name: str) -> Any:
        """Get a service with validation."""
        if not self._initialized:
            raise ConfigurationError(
                "Service manager not initialized",
                error_code="SERVICE_MANAGER_NOT_INITIALIZED"
            )
        
        if service_name not in self.services:
            raise ConfigurationError(
                f"Service not found: {service_name}",
                error_code="SERVICE_NOT_FOUND",
                details={"available_services": list(self.services.keys())}
            )
        
        return self.services[service_name]
    
    def is_service_healthy(self, service_name: str) -> bool:
        """Check if a service is healthy."""
        return self.service_status.get(service_name, False)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        return {
            "initialized": self._initialized,
            "services": self.service_status.copy(),
            "circuit_breakers": {
                name: cb.state.value 
                for name, cb in self.circuit_breakers.items()
            },
            "degraded_services": [
                name for name, status in self.service_status.items() 
                if not status
            ]
        }
    
    async def shutdown(self):
        """Gracefully shutdown all services."""
        logger.info("Shutting down services...")
        
        # Close Redis connection if exists
        if 'redis_client' in self.services and self.services['redis_client']:
            try:
                await self.services['redis_client'].close()
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e}")
        
        self.services.clear()
        self.service_status = {k: False for k in self.service_status}
        self._initialized = False
        
        logger.info("All services shut down")


# Global service manager instance
service_manager = ServiceManager()