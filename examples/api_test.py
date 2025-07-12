# examples/api_test.py
"""
API parallel execution test examples
"""

import parallel_runner
import requests
import time


def simple_api_test():
    """Simple API call test"""
    try:
        response = requests.get("https://httpbin.org/status/200", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def detailed_api_test(endpoint, expected_status=200):
    """Detailed API call test"""
    try:
        start_time = time.time()
        response = requests.get(f"https://httpbin.org/{endpoint}", timeout=10)
        response_time = time.time() - start_time
        
        return {
            "success": response.status_code == expected_status,
            "status_code": response.status_code,
            "response_time": response_time,
            "content_length": len(response.content)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": None
        }


def post_api_test(data):
    """POST API test"""
    try:
        response = requests.post(
            "https://httpbin.org/post",
            json=data,
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


def main():
    print("=== API Parallel Execution Test Examples ===\n")
    
    # Example 1: Distributed execution
    print("1. Distributed execution test (20 times in 30 seconds)")
    summary1 = parallel_runner.distribute("30s", 20, simple_api_test)
    print(f"Success rate: {summary1.success_rate:.1f}%\n")
    
    # Example 2: Burst execution
    print("2. Burst execution test (15 times at once)")
    summary2 = parallel_runner.burst(15, simple_api_test, max_workers=5)
    print(f"Total execution time: {summary2.total_duration:.2f}s")
    print(f"Success rate: {summary2.success_rate:.1f}%\n")
    
    # Example 3: Test with arguments
    print("3. Test with arguments (10 times in 1 minute)")
    runner = parallel_runner.ParallelRunner()
    summary3 = runner.distribute(
        duration="1m",
        count=10,
        target_function=detailed_api_test,
        function_args=("delay/1",),
        function_kwargs={"expected_status": 200}
    )
    print(f"Average response time: {summary3.average_response_time:.3f}s\n")
    
    # Example 4: Progressive execution
    print("4. Progressive execution test")
    stages = [
        (5, "30s"),   # 5 times/30 seconds (warm-up)
        (10, "30s"),  # 10 times/30 seconds (standard)
        (15, "30s"),  # 15 times/30 seconds (peak)
    ]
    
    summaries = parallel_runner.progressive(
        stages=stages,
        target_function=simple_api_test,
        stage_interval=2.0
    )
    
    print("Results by stage:")
    for i, summary in enumerate(summaries, 1):
        print(f"  Stage {i}: Success rate {summary.success_rate:.1f}%, "
              f"RPS {summary.requests_per_second:.2f}")
    
    # Example 5: POST request test
    print("\n5. POST request test (10 times in 45 seconds)")
    test_data = {"test": "data", "timestamp": time.time()}
    
    summary5 = parallel_runner.distribute(
        duration="45s",
        count=10,
        target_function=post_api_test,
        function_args=(test_data,)
    )
    print(f"POST success rate: {summary5.success_rate:.1f}%")


if __name__ == "__main__":
    main()