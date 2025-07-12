# parallel_runner/__init__.py
"""
Parallel Runner - Parallel Execution Library

A simple and flexible library for running parallel execution flows.
Supports various execution patterns like distributed execution, burst execution, and progressive flows.
"""

import time
import concurrent.futures
import uuid
import traceback
import re
from typing import Callable, Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionResult:
    """Single execution result data container"""
    task_id: int
    success: bool
    duration: float
    response_data: Any = None
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionConfig:
    """Execution configuration container"""
    total_requests: int = 100
    duration_hours: float = 0.1  # 6 minutes
    max_workers: int = 10
    request_interval: Optional[float] = None  # Auto-calculated if None


@dataclass
class ExecutionSummary:
    """Execution results summary"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_duration: float
    average_response_time: float
    requests_per_second: float
    success_rate: float
    results: List[ExecutionResult] = field(default_factory=list)


def _parse_duration(duration_str: str) -> float:
    """
    Parse duration string to hours
    
    Examples: "1h" -> 1.0, "30m" -> 0.5, "45s" -> 0.0125
    
    Args:
        duration_str: Duration string like "1h", "30m", "45s"
        
    Returns:
        float: Duration in hours
        
    Raises:
        ValueError: If duration format is invalid
    """
    pattern = r'^(\d+(?:\.\d+)?)(h|m|s)$'
    match = re.match(pattern, duration_str.lower())
    
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}. Use format like '1h', '30m', '45s'")
    
    value, unit = match.groups()
    value = float(value)
    
    if unit == 'h':
        return value
    elif unit == 'm':
        return value / 60.0
    elif unit == 's':
        return value / 3600.0
    
    raise ValueError(f"Unsupported time unit: {unit}")


class ParallelRunner:
    """Main class for managing parallel execution flows"""
    
    def __init__(self, verbose: bool = True):
        """
        Initialize ParallelRunner
        
        Args:
            verbose: Enable verbose logging output
        """
        self.verbose = verbose
        self.results: List[ExecutionResult] = []
    
    def _log(self, message: str):
        """Log output (only when verbose is enabled)"""
        if self.verbose:
            print(message)
    
    def _execute_task(self, task_id: int, target_function: Callable, *args, **kwargs) -> ExecutionResult:
        """
        Execute a single task
        
        Args:
            task_id: Unique task identifier
            target_function: Function to execute
            *args: Positional arguments for target_function
            **kwargs: Keyword arguments for target_function
            
        Returns:
            ExecutionResult: Task execution result
        """
        start_time = time.time()
        
        try:
            result = target_function(*args, **kwargs)
            duration = time.time() - start_time
            
            return ExecutionResult(
                task_id=task_id,
                success=True,
                duration=duration,
                response_data=result
            )
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            
            return ExecutionResult(
                task_id=task_id,
                success=False,
                duration=duration,
                error_message=error_msg
            )
    
    def distribute(
        self,
        duration: str,
        count: int,
        target_function: Callable,
        max_workers: Optional[int] = None,
        function_args: Tuple = (),
        function_kwargs: Dict = None
    ) -> ExecutionSummary:
        """
        Execute specified number of tasks distributed over specified time
        
        Args:
            duration: Execution duration ("1h", "30m", "45s", etc.)
            count: Number of executions
            target_function: Function to execute
            max_workers: Maximum parallel workers (auto-set if None)
            function_args: Positional arguments for target_function
            function_kwargs: Keyword arguments for target_function
            
        Returns:
            ExecutionSummary: Execution results summary
        """
        if function_kwargs is None:
            function_kwargs = {}
        
        # Parse duration
        duration_hours = _parse_duration(duration)
        
        # Auto-set worker count (max 20, min 1)
        if max_workers is None:
            max_workers = min(20, max(1, count // 5))
        
        # Create configuration
        config = ExecutionConfig(
            total_requests=count,
            duration_hours=duration_hours,
            max_workers=max_workers
        )
        
        return self._run_execution_flow(target_function, config, function_args, function_kwargs)
    
    def burst(
        self,
        count: int,
        target_function: Callable,
        max_workers: int = 10,
        function_args: Tuple = (),
        function_kwargs: Dict = None
    ) -> ExecutionSummary:
        """
        Execute specified number of tasks in burst mode (all at once)
        
        Args:
            count: Number of executions
            target_function: Function to execute
            max_workers: Maximum parallel workers
            function_args: Positional arguments for target_function
            function_kwargs: Keyword arguments for target_function
            
        Returns:
            ExecutionSummary: Execution results summary
        """
        if function_kwargs is None:
            function_kwargs = {}
        
        # Burst execution with minimal interval
        config = ExecutionConfig(
            total_requests=count,
            duration_hours=0.001,  # Very short duration for burst
            max_workers=max_workers
        )
        
        return self._run_execution_flow(target_function, config, function_args, function_kwargs)
    
    def _run_execution_flow(
        self,
        target_function: Callable,
        config: ExecutionConfig,
        function_args: Tuple = (),
        function_kwargs: Dict = None
    ) -> ExecutionSummary:
        """
        Execute the main execution flow (internal method)
        
        Args:
            target_function: Function to execute
            config: Execution configuration
            function_args: Positional arguments for target_function
            function_kwargs: Keyword arguments for target_function
            
        Returns:
            ExecutionSummary: Execution results summary
        """
        if function_kwargs is None:
            function_kwargs = {}
        
        # Calculate execution interval
        interval_seconds = (config.duration_hours * 3600) / config.total_requests
        is_burst_mode = interval_seconds < 0.01  # Less than 10ms = burst mode
        
        start_time = time.time()
        scheduled_requests = 0
        
        self._log(f"Execution started: {config.total_requests} executions / {config.duration_hours} hours")
        if not is_burst_mode:
            self._log(f"Average interval: {interval_seconds:.4f}s/execution (theoretical rate: {1/interval_seconds:.2f} executions/sec)")
        else:
            self._log(f"Burst mode: executing all tasks immediately")
        self._log(f"Maximum concurrent workers: {config.max_workers}")
        
        results = []
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=config.max_workers) as executor:
                futures = []
                
                # Schedule all executions
                for i in range(config.total_requests):
                    future = executor.submit(
                        self._execute_task,
                        i + 1,
                        target_function,
                        *function_args,
                        **function_kwargs
                    )
                    futures.append(future)
                    scheduled_requests += 1
                    
                    # Progress display
                    if self.verbose and (scheduled_requests % 100 == 0 or scheduled_requests == config.total_requests):
                        elapsed = time.time() - start_time
                        rate = scheduled_requests / elapsed if elapsed > 0 else 0
                        self._log(f"Scheduled: {scheduled_requests}/{config.total_requests} "
                                f"({scheduled_requests/config.total_requests*100:.1f}%) "
                                f"Schedule rate: {rate:.2f} executions/sec")
                    
                    # Interval control (skip for burst mode)
                    if not is_burst_mode and i < config.total_requests - 1:
                        wait_time = max(0.0, interval_seconds * 0.8)
                        time.sleep(wait_time)
                
                self._log("All executions scheduled. Waiting for completion...")
                
                # Collect results
                completed_count = 0
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                        completed_count += 1
                        
                        # Progress display
                        if self.verbose and completed_count % 100 == 0:
                            success_count = sum(1 for r in results if r.success)
                            elapsed = time.time() - start_time
                            self._log(f"Completed: {completed_count}/{config.total_requests} "
                                    f"Success: {success_count} ({success_count/completed_count*100:.1f}%) "
                                    f"Elapsed time: {elapsed:.1f}s")
                    except Exception as e:
                        self._log(f"Task execution error: {str(e)}")
                        # Create a failed result for the exception
                        results.append(ExecutionResult(
                            task_id=len(results) + 1,
                            success=False,
                            duration=0.0,
                            error_message=f"Future error: {str(e)}"
                        ))
        
        except Exception as e:
            self._log(f"ThreadPoolExecutor error: {e}")
            traceback.print_exc()
        
        # Create summary
        summary = self._create_summary(results, time.time() - start_time)
        self._print_summary(summary)
        
        return summary
    
    def _create_summary(self, results: List[ExecutionResult], total_duration: float) -> ExecutionSummary:
        """
        Create execution results summary
        
        Args:
            results: List of execution results
            total_duration: Total execution time in seconds
            
        Returns:
            ExecutionSummary: Summary of execution results
        """
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        total_requests = len(results)
        successful_requests = len(successful_results)
        failed_requests = len(failed_results)
        
        # Calculate average response time
        if successful_results:
            avg_response_time = sum(r.duration for r in successful_results) / len(successful_results)
        else:
            avg_response_time = 0.0
        
        # Calculate RPS
        requests_per_second = total_requests / total_duration if total_duration > 0 else 0
        
        # Calculate success rate
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        return ExecutionSummary(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_duration=total_duration,
            average_response_time=avg_response_time,
            requests_per_second=requests_per_second,
            success_rate=success_rate,
            results=results
        )
    
    def _print_summary(self, summary: ExecutionSummary):
        """
        Print execution summary
        
        Args:
            summary: Execution summary to print
        """
        if not self.verbose:
            return
            
        self._log("\n===== Execution Results Summary =====")
        self._log(f"Total execution time: {summary.total_duration:.2f}s ({summary.total_duration/3600:.2f}h)")
        self._log(f"Total executions: {summary.total_requests}")
        self._log(f"Successful executions: {summary.successful_requests} ({summary.success_rate:.1f}%)")
        self._log(f"Failed executions: {summary.failed_requests}")
        self._log(f"Average response time: {summary.average_response_time:.3f}s")
        self._log(f"Average execution rate: {summary.requests_per_second:.2f} executions/sec")
        
        # Error summary
        error_summary = {}
        for result in summary.results:
            if not result.success and result.error_message:
                error_type = result.error_message.split(':')[0]
                error_summary[error_type] = error_summary.get(error_type, 0) + 1
        
        if error_summary:
            self._log("\n===== Error Details =====")
            for error_type, count in error_summary.items():
                self._log(f"{error_type}: {count} occurrences")


def progressive(
    stages: List[Tuple[int, str]],  # (count, duration)
    target_function: Callable,
    max_workers: Optional[int] = None,
    function_args: Tuple = (),
    function_kwargs: Dict = None,
    stage_interval: float = 3.0,
    verbose: bool = True
) -> List[ExecutionSummary]:
    """
    Execute progressive execution flow
    
    Args:
        stages: List of (count, duration) tuples (e.g., [(20, "30s"), (50, "30s")])
        target_function: Function to execute
        max_workers: Maximum parallel workers (auto-set if None)
        function_args: Positional arguments for target_function
        function_kwargs: Keyword arguments for target_function
        stage_interval: Wait time between stages (seconds)
        verbose: Enable verbose logging
        
    Returns:
        List[ExecutionSummary]: Results for each stage
    """
    if function_kwargs is None:
        function_kwargs = {}
    
    runner = ParallelRunner(verbose=verbose)
    summaries = []
    
    for i, (count, duration) in enumerate(stages, 1):
        if verbose:
            print(f"\n===== Stage {i}: {count} executions / {duration} =====")
        
        summary = runner.distribute(
            duration=duration,
            count=count,
            target_function=target_function,
            max_workers=max_workers,
            function_args=function_args,
            function_kwargs=function_kwargs
        )
        summaries.append(summary)
        
        # Wait between stages
        if i < len(stages) and stage_interval > 0:
            if verbose:
                print(f"Waiting {stage_interval} seconds...")
            time.sleep(stage_interval)
    
    return summaries


# Convenience functions (module level)
def distribute(
    duration: str,
    count: int,
    target_function: Callable,
    max_workers: Optional[int] = None,
    function_args: Tuple = (),
    function_kwargs: Dict = None,
    verbose: bool = True
) -> ExecutionSummary:
    """
    Execute specified number of tasks distributed over specified time (convenience function)
    
    Args:
        duration: Execution duration ("1h", "30m", "45s", etc.)
        count: Number of executions
        target_function: Function to execute
        max_workers: Maximum parallel workers (auto-set if None)
        function_args: Positional arguments for target_function
        function_kwargs: Keyword arguments for target_function
        verbose: Enable verbose logging
        
    Returns:
        ExecutionSummary: Execution results
    """
    runner = ParallelRunner(verbose=verbose)
    return runner.distribute(
        duration=duration,
        count=count,
        target_function=target_function,
        max_workers=max_workers,
        function_args=function_args,
        function_kwargs=function_kwargs or {}
    )


def burst(
    count: int,
    target_function: Callable,
    max_workers: int = 10,
    function_args: Tuple = (),
    function_kwargs: Dict = None,
    verbose: bool = True
) -> ExecutionSummary:
    """
    Execute specified number of tasks in burst mode (convenience function)
    
    Args:
        count: Number of executions
        target_function: Function to execute
        max_workers: Maximum parallel workers
        function_args: Positional arguments for target_function
        function_kwargs: Keyword arguments for target_function
        verbose: Enable verbose logging
        
    Returns:
        ExecutionSummary: Execution results
    """
    runner = ParallelRunner(verbose=verbose)
    return runner.burst(
        count=count,
        target_function=target_function,
        max_workers=max_workers,
        function_args=function_args,
        function_kwargs=function_kwargs or {}
    )


# Exports
__all__ = [
    'ParallelRunner',
    'ExecutionConfig', 
    'ExecutionSummary',
    'ExecutionResult',
    'distribute',
    'burst',
    'progressive'
]