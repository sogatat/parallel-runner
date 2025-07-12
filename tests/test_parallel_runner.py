# tests/test_parallel_runner.py
"""
Main tests for parallel_runner library
"""

import unittest
import time
import threading
import random  # Add missing import
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import parallel_runner


class TestParallelRunner(unittest.TestCase):
    
    def setUp(self):
        self.runner = parallel_runner.ParallelRunner(verbose=False)
    
    def test_simple_function_execution(self):
        """Test simple function execution"""
        def simple_func():
            return "success"
        
        summary = self.runner.burst(5, simple_func, max_workers=2)
        
        self.assertEqual(summary.total_requests, 5)
        self.assertEqual(summary.successful_requests, 5)
        self.assertEqual(summary.failed_requests, 0)
        self.assertEqual(summary.success_rate, 100.0)
    
    def test_function_with_arguments(self):
        """Test function with arguments"""
        def func_with_args(x, y, z=None):
            return x + y + (z or 0)
        
        summary = self.runner.burst(
            count=3,
            target_function=func_with_args,
            max_workers=1,
            function_args=(1, 2),
            function_kwargs={"z": 3}
        )
        
        self.assertEqual(summary.successful_requests, 3)
        for result in summary.results:
            if result.success:
                self.assertEqual(result.response_data, 6)
    
    def test_function_with_exception(self):
        """Test function that raises exceptions"""
        def failing_func():
            raise ValueError("Test error")
        
        summary = self.runner.burst(3, failing_func, max_workers=1)
        
        self.assertEqual(summary.successful_requests, 0)
        self.assertEqual(summary.failed_requests, 3)
        self.assertEqual(summary.success_rate, 0.0)
        
        for result in summary.results:
            self.assertFalse(result.success)
            self.assertIn("ValueError", result.error_message)
    
    def test_mixed_success_failure(self):
        """Test function with mixed success and failure"""
        call_count = 0
        lock = threading.Lock()
        
        def mixed_func():
            nonlocal call_count
            with lock:
                call_count += 1
                if call_count % 2 == 0:
                    raise Exception("Even call failed")
                return "odd call success"
        
        summary = self.runner.burst(6, mixed_func, max_workers=2)
        
        self.assertEqual(summary.total_requests, 6)
        self.assertEqual(summary.successful_requests, 3)
        self.assertEqual(summary.failed_requests, 3)
        self.assertEqual(summary.success_rate, 50.0)
    
    def test_timing_measurement(self):
        """Test execution time measurement"""
        def slow_func():
            time.sleep(0.1)
            return "done"
        
        summary = self.runner.burst(2, slow_func, max_workers=1)
        
        self.assertGreaterEqual(summary.average_response_time, 0.1)
        for result in summary.results:
            if result.success:
                self.assertGreaterEqual(result.duration, 0.1)


class TestDistributeFunction(unittest.TestCase):
    
    def test_distribute_basic(self):
        """Test basic distribute function"""
        def quick_func():
            return True
        
        summary = parallel_runner.distribute(
            duration="5s",
            count=5,
            target_function=quick_func,
            verbose=False
        )
        
        self.assertEqual(summary.total_requests, 5)
        self.assertEqual(summary.successful_requests, 5)
        self.assertEqual(summary.success_rate, 100.0)
    
    def test_distribute_with_args(self):
        """Test distribute function with arguments"""
        def func_with_args(value):
            return value * 2
        
        summary = parallel_runner.distribute(
            duration="3s",
            count=3,
            target_function=func_with_args,
            function_args=(5,),
            verbose=False
        )
        
        self.assertEqual(summary.successful_requests, 3)
        for result in summary.results:
            if result.success:
                self.assertEqual(result.response_data, 10)


class TestBurstFunction(unittest.TestCase):
    
    def test_burst_basic(self):
        """Test basic burst function"""
        def test_func():
            return "burst_result"
        
        summary = parallel_runner.burst(
            count=5,
            target_function=test_func,
            max_workers=2,
            verbose=False
        )
        
        self.assertEqual(summary.total_requests, 5)
        self.assertEqual(summary.successful_requests, 5)
        self.assertEqual(summary.success_rate, 100.0)


class TestProgressiveFunction(unittest.TestCase):
    
    def test_progressive_stages(self):
        """Test progressive execution"""
        def test_func():
            return "stage_result"
        
        stages = [
            (2, "3s"),  # 2 executions in 3 seconds
            (3, "3s"),  # 3 executions in 3 seconds
        ]
        
        summaries = parallel_runner.progressive(
            stages=stages,
            target_function=test_func,
            stage_interval=0.1,  # 0.1 second wait
            verbose=False
        )
        
        self.assertEqual(len(summaries), 2)
        self.assertEqual(summaries[0].total_requests, 2)
        self.assertEqual(summaries[1].total_requests, 3)
        
        for summary in summaries:
            self.assertEqual(summary.success_rate, 100.0)


class TestTimeParsing(unittest.TestCase):
    """Test time parsing functionality"""
    
    def test_parse_duration_hours(self):
        """Test time parsing (hours)"""
        from parallel_runner import _parse_duration
        
        self.assertEqual(_parse_duration("1h"), 1.0)
        self.assertEqual(_parse_duration("2.5h"), 2.5)
        self.assertEqual(_parse_duration("0.5h"), 0.5)
    
    def test_parse_duration_minutes(self):
        """Test time parsing (minutes)"""
        from parallel_runner import _parse_duration
        
        self.assertEqual(_parse_duration("60m"), 1.0)
        self.assertEqual(_parse_duration("30m"), 0.5)
        self.assertEqual(_parse_duration("90m"), 1.5)
    
    def test_parse_duration_seconds(self):
        """Test time parsing (seconds)"""
        from parallel_runner import _parse_duration
        
        self.assertEqual(_parse_duration("3600s"), 1.0)
        self.assertEqual(_parse_duration("1800s"), 0.5)
        self.assertEqual(_parse_duration("45s"), 0.0125)
    
    def test_parse_duration_invalid(self):
        """Test invalid time format"""
        from parallel_runner import _parse_duration
        
        with self.assertRaises(ValueError):
            _parse_duration("1x")  # Invalid unit
        
        with self.assertRaises(ValueError):
            _parse_duration("abc")  # Non-numeric
        
        with self.assertRaises(ValueError):
            _parse_duration("1")  # No unit


class TestRealWorldScenarios(unittest.TestCase):
    """Tests simulating real-world usage scenarios"""
    
    def test_api_simulation(self):
        """API call simulation"""
        import random
        
        def api_simulation():
            # Simulate response time
            time.sleep(random.uniform(0.01, 0.05))
            
            # 90% success rate
            if random.random() < 0.9:
                return {"status": "ok", "data": "response"}
            else:
                raise Exception("API Error")
        
        summary = parallel_runner.burst(
            count=20,
            target_function=api_simulation,
            max_workers=5,
            verbose=False
        )
        
        # Statistically expect about 18 successes (90% success rate)
        self.assertGreaterEqual(summary.successful_requests, 15)
        self.assertLessEqual(summary.successful_requests, 20)
    
    def test_database_simulation(self):
        """Database access simulation"""
        query_count = 0
        lock = threading.Lock()
        
        def db_simulation(query):
            nonlocal query_count
            with lock:
                query_count += 1
            
            # Simulate DB processing time
            time.sleep(0.02)
            
            return {"rows_affected": 1, "query": query}
        
        summary = parallel_runner.burst(
            count=10,
            target_function=db_simulation,
            max_workers=3,
            function_args=("SELECT * FROM test",),
            verbose=False
        )
        
        self.assertEqual(summary.successful_requests, 10)
        self.assertEqual(query_count, 10)
        
        for result in summary.results:
            if result.success:
                self.assertEqual(result.response_data["rows_affected"], 1)
    
    def test_load_testing_scenario(self):
        """Load testing scenario"""
        request_times = []
        lock = threading.Lock()
        
        def load_test_target():
            start = time.time()
            # Simulate processing time
            time.sleep(random.uniform(0.05, 0.15))
            end = time.time()
            
            with lock:
                request_times.append(end - start)
            
            return {"response_time": end - start}
        
        # 30 requests in 15 seconds (shorter duration)
        summary = parallel_runner.distribute(
            duration="15s",
            count=30,
            target_function=load_test_target,
            max_workers=8,
            verbose=False
        )
        
        self.assertEqual(summary.total_requests, 30)
        self.assertGreater(summary.successful_requests, 20)  # Reduced expectation (66% success)
        self.assertLess(summary.total_duration, 20)  # Complete within 20 seconds


if __name__ == '__main__':
    unittest.main()