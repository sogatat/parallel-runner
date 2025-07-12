#!/usr/bin/env python3
# tests/run_tests.py
"""
Test execution script - convenient test runner for development
"""

import unittest
import sys
import os
import time
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import with debug information
try:
    import parallel_runner
    print(f"✓ parallel_runner imported from: {parallel_runner.__file__}")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Project root: {project_root}")
    
    # Try fallback import method
    try:
        sys.path.append(str(project_root / "parallel_runner"))
        import __init__ as parallel_runner
        print("✓ Fallback import successful")
    except ImportError:
        print("❌ Fallback import also failed")
        sys.exit(1)


def discover_and_run_tests(pattern="test*.py", verbosity=2, failfast=False):
    """Discover and run tests automatically"""
    test_dir = Path(__file__).parent
    
    loader = unittest.TestLoader()
    start_dir = str(test_dir)
    suite = loader.discover(start_dir, pattern=pattern)
    
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        buffer=True
    )
    
    print(f"Running tests from: {test_dir}")
    print(f"Pattern: {pattern}")
    print("=" * 70)
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    print("=" * 70)
    print(f"Tests completed in {end_time - start_time:.2f} seconds")
    
    return result.wasSuccessful()


def run_specific_test(test_name, verbosity=2):
    """Run specific test class or method"""
    try:
        # Support test_module.TestClass.test_method format
        parts = test_name.split('.')
        
        if len(parts) == 1:
            # Module name only
            module_name = f"test_{parts[0]}"
            suite = unittest.TestLoader().loadTestsFromName(module_name)
        elif len(parts) == 2:
            # module.class
            module_name, class_name = parts
            suite = unittest.TestLoader().loadTestsFromName(
                f"{module_name}.{class_name}"
            )
        elif len(parts) == 3:
            # module.class.method
            module_name, class_name, method_name = parts
            suite = unittest.TestLoader().loadTestsFromName(
                f"{module_name}.{class_name}.{method_name}"
            )
        else:
            print(f"Invalid test name format: {test_name}")
            return False
        
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"Error running test {test_name}: {e}")
        return False


def run_quick_smoke_test():
    """Quick smoke test - verify basic functionality works"""
    print("Running quick smoke test...")
    print("=" * 50)
    
    try:
        # Basic import test
        print("✓ Import test passed")
        
        # Simple execution test
        def simple_task():
            return "success"
        
        summary = parallel_runner.burst(5, simple_task, verbose=False)
        assert summary.success_rate == 100.0
        print("✓ Basic execution test passed")
        
        # Distributed execution test
        summary = parallel_runner.distribute("5s", 3, simple_task, verbose=False)
        assert summary.success_rate == 100.0
        print("✓ Distribute execution test passed")
        
        # Progressive execution test
        stages = [(2, "3s"), (3, "3s")]
        summaries = parallel_runner.progressive(stages, simple_task, verbose=False)
        assert len(summaries) == 2
        print("✓ Progressive execution test passed")
        
        print("=" * 50)
        print("🎉 All smoke tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False


def run_performance_benchmark():
    """Run performance benchmark"""
    print("Running performance benchmark...")
    print("=" * 50)
    
    def cpu_task():
        return sum(range(1000))
    
    def io_task():
        time.sleep(0.01)
        return "io_complete"
    
    tasks = [
        ("CPU Task", cpu_task),
        ("I/O Task", io_task),
    ]
    
    for task_name, task_func in tasks:
        print(f"\n--- {task_name} ---")
        
        for workers in [1, 5, 10]:
            summary = parallel_runner.burst(
                count=20,
                target_function=task_func,
                max_workers=workers,
                verbose=False
            )
            
            print(f"Workers: {workers:2d} | "
                  f"RPS: {summary.requests_per_second:6.2f} | "
                  f"Avg: {summary.average_response_time:.4f}s")


def check_test_coverage():
    """Check test coverage (requires coverage.py)"""
    try:
        import coverage
        
        print("Running tests with coverage...")
        cov = coverage.Coverage()
        cov.start()
        
        # Run tests
        success = discover_and_run_tests(verbosity=1)
        
        cov.stop()
        cov.save()
        
        print("\nCoverage Report:")
        cov.report(show_missing=True)
        
        return success
        
    except ImportError:
        print("Coverage.py not installed. Run: pip install coverage")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Parallel Runner Test Suite")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["all", "smoke", "benchmark", "coverage", "specific"],
        default="all",
        help="Test command to run"
    )
    parser.add_argument(
        "--test",
        help="Specific test to run (use with 'specific' command)"
    )
    parser.add_argument(
        "--pattern",
        default="test*.py",
        help="Test file pattern"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=2,
        help="Increase verbosity"
    )
    parser.add_argument(
        "--failfast", "-f",
        action="store_true",
        help="Stop on first failure"
    )
    
    args = parser.parse_args()
    
    print(f"Parallel Runner Test Suite")
    print(f"Python: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    success = True
    
    if args.command == "all":
        success = discover_and_run_tests(
            pattern=args.pattern,
            verbosity=args.verbose,
            failfast=args.failfast
        )
    
    elif args.command == "smoke":
        success = run_quick_smoke_test()
    
    elif args.command == "benchmark":
        run_performance_benchmark()
    
    elif args.command == "coverage":
        success = check_test_coverage()
    
    elif args.command == "specific":
        if not args.test:
            print("Error: --test argument required for 'specific' command")
            return 1
        success = run_specific_test(args.test, args.verbose)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)