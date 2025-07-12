# Parallel Runner

A simple and flexible Python library for running parallel execution flows.
Supports various execution patterns like distributed execution, burst execution, and progressive flows.

## Installation

```bash
pip install parallel-runner
```

## Basic Usage

### 1. Distributed Execution - `distribute()`

Execute a specified number of tasks distributed over a specified time period.

```python
import parallel_runner
import requests
import time

def api_test():
    """Target API call for execution"""
    response = requests.get("https://httpbin.org/delay/1")
    return response.status_code == 200

# Execute 50 times distributed over 1 hour
summary = parallel_runner.distribute("1h", 50, api_test)

# Execute 100 times distributed over 30 minutes
summary = parallel_runner.distribute("30m", 100, api_test)

# Execute 20 times distributed over 45 seconds
summary = parallel_runner.distribute("45s", 20, api_test)

print(f"Success rate: {summary.success_rate:.1f}%")
print(f"Average response time: {summary.average_response_time:.3f}s")
```

### 2. Burst Execution - `burst()`

Execute a specified number of tasks all at once in burst mode.

```python
import parallel_runner

def quick_task():
    time.sleep(0.1)  # Simulate processing time
    return "success"

# Execute 100 tasks at once (10 workers)
summary = parallel_runner.burst(100, quick_task, max_workers=10)

print(f"Total execution time: {summary.total_duration:.2f}s")
print(f"Success rate: {summary.success_rate:.1f}%")
```

### 3. Class-based Detailed Control

```python
import parallel_runner

def custom_function(user_id, api_key):
    """Example function with arguments"""
    # API call or other processing
    time.sleep(0.1)  # Simulate processing time
    return {"user_id": user_id, "status": "success"}

# Detailed control with ParallelRunner class
runner = parallel_runner.ParallelRunner(verbose=True)

# Distributed execution
summary = runner.distribute(
    duration="30m",
    count=100,
    target_function=custom_function,
    max_workers=20,
    function_args=("user123",),          # Positional arguments
    function_kwargs={"api_key": "key456"} # Keyword arguments
)

# Burst execution
summary = runner.burst(
    count=50,
    target_function=custom_function,
    max_workers=15,
    function_args=("user456",),
    function_kwargs={"api_key": "key789"}
)

# Detailed result analysis
for result in summary.results:
    if not result.success:
        print(f"Error: {result.error_message}")
```

### 4. Progressive Execution - `progressive()`

Execute multiple stages progressively.

```python
import parallel_runner

def simple_task():
    time.sleep(0.05)  # 50ms processing simulation
    return "success"

# Stage definition: (execution_count, duration)
stages = [
    (20, "30s"),   # Warm-up: 20 executions/30 seconds
    (50, "30s"),   # Standard load: 50 executions/30 seconds  
    (100, "30s"),  # Peak load: 100 executions/30 seconds
]

summaries = parallel_runner.progressive(
    stages=stages,
    target_function=simple_task,
    stage_interval=3.0  # 3 seconds wait between stages
)

# Check results for each stage
for i, summary in enumerate(summaries, 1):
    print(f"Stage {i}: Success rate {summary.success_rate:.1f}%, RPS {summary.requests_per_second:.2f}")
```

### 5. Web API Testing Example

```python
import parallel_runner
import requests
import json

def test_api_endpoint(base_url, endpoint, method="GET", payload=None):
    """Generic API test function"""
    url = f"{base_url}/{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=payload, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return {
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "success": 200 <= response.status_code < 300
        }
    except Exception as e:
        return {
            "status_code": None,
            "response_time": None,
            "success": False,
            "error": str(e)
        }

# API load testing - 200 times in 1 hour
summary = parallel_runner.distribute(
    duration="1h",
    count=200,
    target_function=test_api_endpoint,
    max_workers=25,
    function_args=("https://jsonplaceholder.typicode.com", "posts/1"),
    function_kwargs={"method": "GET"}
)

print(f"API test completed:")
print(f"- Total executions: {summary.total_requests}")
print(f"- Success: {summary.successful_requests} ({summary.success_rate:.1f}%)")
print(f"- Average response time: {summary.average_response_time:.3f}s")
print(f"- RPS: {summary.requests_per_second:.2f}")
```

### 6. Database Access Testing

```python
import parallel_runner
import sqlite3
import threading

# Thread local storage for DB connections
thread_local = threading.local()

def get_db_connection():
    """Get DB connection per thread"""
    if not hasattr(thread_local, 'connection'):
        thread_local.connection = sqlite3.connect('test.db')
    return thread_local.connection

def database_operation(query, params=None):
    """Database operation test"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = cursor.fetchall()
        conn.commit()
        return len(result)
    except Exception as e:
        return False

# Database access testing - 500 times in 5 minutes
summary = parallel_runner.distribute(
    duration="5m",
    count=500,
    target_function=database_operation,
    max_workers=10,
    function_args=("SELECT * FROM users WHERE id = ?",),
    function_kwargs={"params": (1,)}
)
```

## Time Format

Time can be specified in the following formats:

- `"1h"` - 1 hour
- `"30m"` - 30 minutes  
- `"45s"` - 45 seconds
- `"2.5h"` - 2 hours 30 minutes
- `"90m"` - 90 minutes (1 hour 30 minutes)

## API Reference

### Function Level API

```python
# Distributed execution
parallel_runner.distribute(duration, count, target_function, **options)

# Burst execution  
parallel_runner.burst(count, target_function, **options)

# Progressive execution
parallel_runner.progressive(stages, target_function, **options)
```

### Class-based API

```python
runner = parallel_runner.ParallelRunner(verbose=True)

# Distributed execution
runner.distribute(duration, count, target_function, **options)

# Burst execution
runner.burst(count, target_function, **options)
```

### ExecutionConfig
Defines execution configuration.

- `total_requests`: Total number of executions
- `duration_hours`: Execution time (in hours)
- `max_workers`: Maximum parallel workers

### ExecutionResult
Stores individual execution results.

- `task_id`: Task ID
- `success`: Success/failure status
- `duration`: Execution time
- `response_data`: Response data
- `error_message`: Error message
- `timestamp`: Execution timestamp

### ExecutionSummary
Summary of overall execution results.

- `total_requests`: Total number of executions
- `successful_requests`: Number of successful executions
- `failed_requests`: Number of failed executions
- `total_duration`: Total execution time
- `average_response_time`: Average response time
- `requests_per_second`: Executions per second
- `success_rate`: Success rate (%)
- `results`: List of individual results

## Package Structure

```
parallel-runner/
├── parallel_runner/
│   └── __init__.py
├── setup.py
├── README.md
├── LICENSE
└── examples/
    ├── api_test.py
    ├── database_test.py
    └── progressive_test.py
```

## Development

### Development Environment Setup

```bash
git clone https://github.com/sogatat/parallel-runner.git
cd parallel-runner
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black parallel_runner/
flake8 parallel_runner/
```

## License

MIT License

## Authors

**Tasuya-SOGA**  
📧 sogatat@gmail.com  
🐙 [GitHub](https://github.com/sogatat)

**Masaki Yamamoto**  
📧 masaki.yamamoto373@gmail.com

## Contributing

Pull requests and issues are welcome.

## Support

If you find this library helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs via GitHub Issues
- 💡 Suggesting new features
- 📖 Improving documentation

## Languages

- [English](README.md) (Current)
- [日本語](README-ja.md)