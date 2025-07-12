# 開発用コマンド集

## tests/ ディレクトリの構成

```
tests/
├── __init__.py
├── test_parallel_runner.py      # メインの機能テスト
├── test_integration.py          # 統合テスト（実用的なシナリオ）
├── test_development_tools.py    # 開発支援・デバッグツール
└── run_tests.py                 # テスト実行スクリプト
```

## テスト実行方法

### 1. 基本的なテスト実行

```bash
# 全テスト実行
python tests/run_tests.py all

# または標準的なpytest
pytest tests/

# または unittest
python -m unittest discover tests/
```

### 2. 特定用途別テスト

```bash
# スモークテスト（基本機能確認）
python tests/run_tests.py smoke

# パフォーマンスベンチマーク
python tests/run_tests.py benchmark

# カバレッジ付きテスト
python tests/run_tests.py coverage

# 特定のテストクラス
python tests/run_tests.py specific --test test_parallel_runner.TestParallelRunner

# 特定のテストメソッド
python tests/run_tests.py specific --test test_parallel_runner.TestParallelRunner.test_simple_function_execution
```

### 3. 開発支援ツール

```bash
# 開発用テストスイート実行
python tests/test_development_tools.py dev

# 詳細なデバッグ情報付きテスト
python tests/run_tests.py all --verbose 3

# 最初の失敗で停止
python tests/run_tests.py all --failfast
```

## Makefile (開発用ショートカット)

```makefile
# Makefile
.PHONY: test smoke benchmark coverage clean install dev-install format lint

# 基本テスト
test:
	python tests/run_tests.py all

# スモークテスト
smoke:
	python tests/run_tests.py smoke

# ベンチマーク
benchmark:
	python tests/run_tests.py benchmark

# カバレッジ
coverage:
	python tests/run_tests.py coverage

# フォーマット
format:
	black parallel_runner/ tests/ examples/
	
# リント
lint:
	flake8 parallel_runner/ tests/ examples/

# 開発用インストール
dev-install:
	pip install -e ".[dev]"

# クリーンアップ
clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info/

# 全開発チェック
check: format lint test

# パッケージビルド
build:
	python setup.py sdist bdist_wheel

# パッケージのテストアップロード
test-upload:
	twine upload --repository testpypi dist/*

# パッケージの本番アップロード
upload:
	twine upload dist/*
```

## 開発ワークフロー用スクリプト

### dev.sh (Unix/Linux/macOS)

```bash
#!/bin/bash
# dev.sh - 開発用スクリプト

set -e

case "$1" in
    "setup")
        echo "Setting up development environment..."
        python -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -e ".[dev]"
        echo "✓ Development environment ready!"
        ;;
    
    "test")
        echo "Running all tests..."
        python tests/run_tests.py all
        ;;
    
    "quick")
        echo "Quick validation..."
        python tests/run_tests.py smoke
        black --check parallel_runner/ tests/
        flake8 parallel_runner/ tests/
        echo "✓ Quick validation passed!"
        ;;
    
    "format")
        echo "Formatting code..."
        black parallel_runner/ tests/ examples/
        echo "✓ Code formatted!"
        ;;
    
    "lint")
        echo "Running linter..."
        flake8 parallel_runner/ tests/ examples/
        echo "✓ Linting passed!"
        ;;
    
    "coverage")
        echo "Running tests with coverage..."
        python tests/run_tests.py coverage
        ;;
    
    "benchmark")
        echo "Running performance benchmark..."
        python tests/run_tests.py benchmark
        ;;
    
    "clean")
        echo "Cleaning up..."
        find . -type d -name __pycache__ -delete
        find . -type f -name "*.pyc" -delete
        rm -rf build/ dist/ *.egg-info/
        echo "✓ Cleaned up!"
        ;;
    
    "build")
        echo "Building package..."
        ./dev.sh clean
        python setup.py sdist bdist_wheel
        echo "✓ Package built!"
        ;;
    
    "check")
        echo "Full development check..."
        ./dev.sh format
        ./dev.sh lint  
        ./dev.sh test
        echo "✓ All checks passed!"
        ;;
    
    *)
        echo "Usage: $0 {setup|test|quick|format|lint|coverage|benchmark|clean|build|check}"
        echo ""
        echo "Commands:"
        echo "  setup      - Set up development environment"
        echo "  test       - Run all tests"
        echo "  quick      - Quick validation (smoke test + format + lint)"
        echo "  format     - Format code with black"
        echo "  lint       - Run flake8 linter"
        echo "  coverage   - Run tests with coverage"
        echo "  benchmark  - Run performance benchmark"
        echo "  clean      - Clean up temporary files"
        echo "  build      - Build package"
        echo "  check      - Full development check"
        exit 1
        ;;
esac
```

### dev.bat (Windows)

```batch
@echo off
rem dev.bat - Windows開発用スクリプト

if "%1"=="setup" (
    echo Setting up development environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -e ".[dev]"
    echo ✓ Development environment ready!
    goto :eof
)

if "%1"=="test" (
    echo Running all tests...
    python tests\run_tests.py all
    goto :eof
)

if "%1"=="quick" (
    echo Quick validation...
    python tests\run_tests.py smoke
    black --check parallel_runner\ tests\
    flake8 parallel_runner\ tests\
    echo ✓ Quick validation passed!
    goto :eof
)

if "%1"=="format" (
    echo Formatting code...
    black parallel_runner\ tests\ examples\
    echo ✓ Code formatted!
    goto :eof
)

if "%1"=="clean" (
    echo Cleaning up...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    del /s /q *.pyc 2>nul
    rd /s /q build 2>nul
    rd /s /q dist 2>nul
    echo ✓ Cleaned up!
    goto :eof
)

echo Usage: %0 {setup^|test^|quick^|format^|clean}
echo.
echo Commands:
echo   setup      - Set up development environment
echo   test       - Run all tests
echo   quick      - Quick validation
echo   format     - Format code
echo   clean      - Clean up temporary files
```

## 使用方法

```bash
# Unix/Linux/macOS
chmod +x dev.sh

# 開発環境セットアップ
./dev.sh setup

# 日常の開発チェック
./dev.sh quick

# 全チェック（コミット前）
./dev.sh check

# Windows
# 開発環境セットアップ
dev.bat setup

# クイックチェック
dev.bat quick
```

これらのスクリプトにより、開発作業が大幅に効率化されます！