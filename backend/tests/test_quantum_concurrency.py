import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

# Add the shared services to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'services'))

from quantum_optimization_service import QuantumOptimizationService, PortfolioAsset

class TestQuantumConcurrency:
    """Test quantum optimization service concurrency features"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = QuantumOptimizationService()
        
        # Create test assets
        self.test_assets = [
            PortfolioAsset(
                symbol="AAPL",
                weight=0.3,
                expected_return=0.12,
                volatility=0.25,
                sector="Technology",
                region="US",
                esg_score=0.8
            ),
            PortfolioAsset(
                symbol="MSFT",
                weight=0.3,
                expected_return=0.15,
                volatility=0.22,
                sector="Technology",
                region="US",
                esg_score=0.85
            ),
            PortfolioAsset(
                symbol="GOOGL",
                weight=0.2,
                expected_return=0.18,
                volatility=0.28,
                sector="Technology",
                region="US",
                esg_score=0.75
            ),
            PortfolioAsset(
                symbol="TSLA",
                weight=0.2,
                expected_return=0.25,
                volatility=0.45,
                sector="Automotive",
                region="US",
                esg_score=0.9
            )
        ]
    
    def test_concurrent_optimization_initialization(self):
        """Test that concurrent optimization service initializes correctly"""
        assert hasattr(self.service, 'thread_pool')
        assert hasattr(self.service, 'optimization_lock')
        assert self.service.thread_pool is not None
    
    def test_optimize_chunk_success(self):
        """Test successful optimization of a single chunk"""
        chunk = self.test_assets[:2]  # First 2 assets
        
        result = self.service._optimize_chunk(
            chunk, target_return=0.15, risk_tolerance=0.5, max_iterations=100, chunk_id=0
        )
        
        assert "error" not in result
        assert result["chunk_id"] == 0
        assert result["status"] == "success"
        assert len(result["weights"]) == 2
        assert abs(sum(result["weights"]) - 1.0) < 0.001  # Weights sum to 1
    
    def test_optimize_chunk_empty_assets(self):
        """Test optimization with empty asset list"""
        result = self.service._optimize_chunk(
            [], target_return=0.15, risk_tolerance=0.5, max_iterations=100, chunk_id=0
        )
        
        assert "error" in result
        assert result["chunk_id"] == 0
    
    def test_combine_chunk_results_success(self):
        """Test successful combination of chunk results"""
        chunk_results = [
            {
                "chunk_id": 0,
                "assets": ["AAPL", "MSFT"],
                "weights": [0.6, 0.4],
                "expected_return": 0.13,
                "volatility": 0.23,
                "status": "success"
            },
            {
                "chunk_id": 1,
                "assets": ["GOOGL", "TSLA"],
                "weights": [0.5, 0.5],
                "expected_return": 0.21,
                "volatility": 0.36,
                "status": "success"
            }
        ]
        
        result = self.service._combine_chunk_results(chunk_results, self.test_assets)
        
        assert "error" not in result
        assert result["optimization_method"] == "concurrent_classical"
        assert result["total_assets"] == 4
        assert result["chunks_processed"] == 2
        assert len(result["weights"]) == 4
    
    def test_combine_chunk_results_all_failed(self):
        """Test combination when all chunks fail"""
        chunk_results = [
            {"chunk_id": 0, "error": "Optimization failed"},
            {"chunk_id": 1, "error": "Optimization failed"}
        ]
        
        result = self.service._combine_chunk_results(chunk_results, self.test_assets)
        
        assert "error" in result
        assert "All optimization chunks failed" in result["error"]
    
    def test_concurrent_optimization_integration(self):
        """Test the full concurrent optimization pipeline"""
        result = self.service.optimize_portfolio_concurrent(
            self.test_assets,
            target_return=0.15,
            risk_tolerance=0.5,
            max_iterations=100
        )
        
        assert "error" not in result
        assert result["optimization_method"] == "concurrent_classical"
        assert result["total_assets"] == 4
        assert len(result["weights"]) == 4
        assert abs(sum(result["weights"]) - 1.0) < 0.001
    
    def test_concurrent_optimization_empty_assets(self):
        """Test concurrent optimization with empty asset list"""
        result = self.service.optimize_portfolio_concurrent(
            [],
            target_return=0.15,
            risk_tolerance=0.5,
            max_iterations=100
        )
        
        assert "error" in result
        assert "No assets provided" in result["error"]
    
    def test_cleanup_method(self):
        """Test that cleanup method works correctly"""
        # This test verifies the cleanup method exists and can be called
        assert hasattr(self.service, 'cleanup')
        
        # Mock the thread pool to avoid actual shutdown during testing
        with patch.object(self.service.thread_pool, 'shutdown') as mock_shutdown:
            self.service.cleanup()
            mock_shutdown.assert_called_once_with(wait=True)
    
    def test_thread_pool_executor_usage(self):
        """Test that thread pool executor is properly configured"""
        assert self.service.thread_pool._max_workers == 4
        
        # Test that we can submit a simple task
        future = self.service.thread_pool.submit(lambda x: x * 2, 5)
        result = future.result(timeout=5)
        assert result == 10
    
    def test_optimization_lock_thread_safety(self):
        """Test that optimization lock provides thread safety"""
        import threading
        import time
        
        results = []
        lock_acquired = threading.Event()
        
        def worker_function():
            with self.service.optimization_lock:
                lock_acquired.set()
                time.sleep(0.1)  # Simulate work
                results.append(threading.current_thread().ident)
        
        # Start two threads
        thread1 = threading.Thread(target=worker_function)
        thread2 = threading.Thread(target=worker_function)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Verify both threads executed
        assert len(results) == 2
        assert results[0] != results[1]  # Different thread IDs
    
    def teardown_method(self):
        """Clean up after tests"""
        if hasattr(self.service, 'cleanup'):
            self.service.cleanup()
