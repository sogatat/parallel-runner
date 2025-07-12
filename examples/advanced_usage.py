# examples/advanced_usage.py
"""
Advanced usage examples
"""

import parallel_runner
import time
import random
import threading
from typing import Dict, Any


# Example 1: Custom metrics collection
class CustomMetricsCollector:
    def __init__(self):
        self.lock = threading.Lock()
        self.custom_metrics = []
    
    def collect_metric(self, metric_data):
        with self.lock:
            self.custom_metrics.append(metric_data)

collector = CustomMetricsCollector()

def api_with_custom_metrics(endpoint_id: int) -> Dict[str, Any]:
    """API call with custom metrics collection"""
    start_time = time.time()
    
    # Simulate API call
    processing_time = random.uniform(0.1, 0.5)
    time.sleep(processing_time)
    
    # Random success/failure (90% success rate)
    success = random.random() < 0.9
    
    end_time = time.time()
    
    # Collect custom metrics
    metric_data = {
        'endpoint_id': endpoint_id,
        'processing_time': processing_time,
        'total_time': end_time - start_time,
        'timestamp': end_time,
        'success': success
    }
    collector.collect_metric(metric_data)
    
    if not success:
        raise Exception(f"API Error for endpoint {endpoint_id}")
    
    return {'endpoint_id': endpoint_id, 'result': 'success'}


# Example 2: Resource pool usage in load testing
class ConnectionPool:
    def __init__(self, pool_size: int = 10):
        self.pool = [f"connection_{i}" for i in range(pool_size)]
        self.lock = threading.Lock()
        self.available = set(self.pool)
        self.in_use = set()
    
    def get_connection(self):
        with self.lock:
            if not self.available:
                return None
            connection = self.available.pop()
            self.in_use.add(connection)
            return connection
    
    def release_connection(self, connection):
        with self.lock:
            if connection in self.in_use:
                self.in_use.remove(connection)
                self.available.add(connection)

# Global pool
connection_pool = ConnectionPool(5)

def database_operation_with_pool(query: str) -> bool:
    """Database operation simulation using connection pool"""
    # Get connection
    conn = connection_pool.get_connection()
    if not conn:
        raise Exception("No available connections")
    
    try:
        # Simulate DB operation
        time.sleep(random.uniform(0.05, 0.2))
        
        # 5% chance of error
        if random.random() < 0.05:
            raise Exception("Database error")
        
        return True
    finally:
        # Always return connection
        connection_pool.release_connection(conn)


# Example 3: Rate-limited API
class RateLimiter:
    def __init__(self, max_requests_per_second: float):
        self.max_rps = max_requests_per_second
        self.lock = threading.Lock()
        self.requests = []
    
    def acquire(self) -> bool:
        now = time.time()
        
        with self.lock:
            # Remove requests older than 1 second
            self.requests = [req_time for req_time in self.requests if now - req_time <= 1.0]
            
            # Check rate limit
            if len(self.requests) >= self.max_rps:
                return False
            
            self.requests.append(now)
            return True

rate_limiter = RateLimiter(10.0)  # 10 requests per second limit

def rate_limited_api() -> bool:
    """Rate-limited API call"""
    if not rate_limiter.acquire():
        raise Exception("Rate limit exceeded")
    
    # Simulate API call
    time.sleep(random.uniform(0.1, 0.3))
    return True


# Example 4: Retry logic for failures
def api_with_retry(max_retries: int = 3) -> Dict[str, Any]:
    """API call with retry logic"""
    for attempt in range(max_retries + 1):
        try:
            # 70% chance of success
            if random.random() < 0.7:
                time.sleep(0.1)  # Normal processing time
                return {'status': 'success', 'attempt': attempt + 1}
            else:
                raise Exception(f"API failed on attempt {attempt + 1}")
        
        except Exception as e:
            if attempt == max_retries:
                # Last attempt also failed
                raise e
            # Wait before retry
            time.sleep(0.1 * (attempt + 1))  # Exponential backoff


def run_advanced_examples():
    """Run advanced usage examples"""
    print("=== Advanced Usage Examples ===\n")
    
    # Example 1: Custom metrics
    print("1. Custom metrics collection test")
    summary1 = parallel_runner.burst(
        count=20,
        target_function=api_with_custom_metrics,
        max_workers=5,
        function_args=(1,),  # endpoint_id
        verbose=False
    )
    
    print(f"Basic results: Success rate {summary1.success_rate:.1f}%")
    print(f"Custom metrics collected: {len(collector.custom_metrics)}")
    
    # Custom metrics analysis
    if collector.custom_metrics:
        avg_processing = sum(m['processing_time'] for m in collector.custom_metrics) / len(collector.custom_metrics)
        print(f"Average processing time: {avg_processing:.3f}s\n")
    
    # Example 2: Connection pool
    print("2. Connection pool test")
    summary2 = parallel_runner.burst(
        count=15,
        target_function=database_operation_with_pool,
        max_workers=8,  # More workers than pool size (5)
        function_args=("SELECT * FROM users",),
        verbose=False
    )
    print(f"Connection pool results: Success rate {summary2.success_rate:.1f}%\n")
    
    # Example 3: Rate limiting
    print("3. Rate limiting test")
    summary3 = parallel_runner.burst(
        count=25,
        target_function=rate_limited_api,
        max_workers=15,  # More workers than rate limit (10rps)
        verbose=False
    )
    print(f"Rate limiting results: Success rate {summary3.success_rate:.1f}%")
    
    # Failed request details
    failed_results = [r for r in summary3.results if not r.success]
    rate_limit_errors = sum(1 for r in failed_results if "Rate limit" in r.error_message)
    print(f"Rate limit errors: {rate_limit_errors} occurrences\n")
    
    # Example 4: Retry logic
    print("4. Retry logic test")
    summary4 = parallel_runner.burst(
        count=20,
        target_function=api_with_retry,
        max_workers=5,
        function_kwargs={"max_retries": 2},
        verbose=False
    )
    print(f"Retry logic results: Success rate {summary4.success_rate:.1f}%")
    
    # Analyze attempt counts for successful requests
    successful_results = [r for r in summary4.results if r.success and r.response_data]
    if successful_results:
        attempts = [r.response_data.get('attempt', 1) for r in successful_results]
        avg_attempts = sum(attempts) / len(attempts)
        print(f"Average attempts: {avg_attempts:.1f}\n")
    
    # Example 5: Progressive load test (realistic scaling scenario)
    print("5. Realistic progressive load test")
    
    def simple_api():
        time.sleep(0.1)
        return random.random() < 0.95  # 95% success rate
    
    # Real scaling pattern
    scaling_stages = [
        (10, "1m"),   # 10req/1min (warm-up)
        (20, "1m"),   # 20req/1min (normal load)
        (40, "1m"),   # 40req/1min (high load)
        (60, "1m"),   # 60req/1min (peak load)
    ]
    
    scaling_summaries = parallel_runner.progressive(
        stages=scaling_stages,
        target_function=simple_api,
        stage_interval=3.0,
        verbose=False
    )
    
    print("Scaling results:")
    for i, summary in enumerate(scaling_summaries, 1):
        print(f"  Stage {i}: {summary.total_requests}req, "
              f"success rate {summary.success_rate:.1f}%, "
              f"RPS {summary.requests_per_second:.2f}, "
              f"avg response {summary.average_response_time:.3f}s")


if __name__ == "__main__":
    run_advanced_examples()