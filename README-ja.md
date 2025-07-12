# Parallel Runner

並列実行フローを実行するためのシンプルで柔軟なPythonライブラリです。
分散実行、バースト実行、段階的実行など、様々な実行パターンをサポートしています。

## インストール

```bash
pip install parallel-runner
```

## 基本的な使用方法

### 1. 分散実行 - `distribute()`

指定した時間内に指定回数を分散して実行します。

```python
import parallel_runner
import requests
import time

def api_test():
    """実行対象のAPI呼び出し"""
    response = requests.get("https://httpbin.org/delay/1")
    return response.status_code == 200

# 1時間に50回分散実行
summary = parallel_runner.distribute("1h", 50, api_test)

# 30分に100回分散実行
summary = parallel_runner.distribute("30m", 100, api_test)

# 45秒に20回分散実行
summary = parallel_runner.distribute("45s", 20, api_test)

print(f"成功率: {summary.success_rate:.1f}%")
print(f"平均レスポンス時間: {summary.average_response_time:.3f}秒")
```

### 2. バースト実行 - `burst()`

指定回数を一気にバースト実行します。

```python
import parallel_runner

def quick_task():
    time.sleep(0.1)  # 処理時間をシミュレート
    return "success"

# 100回を一気に実行（10並列）
summary = parallel_runner.burst(100, quick_task, max_workers=10)

print(f"総実行時間: {summary.total_duration:.2f}秒")
print(f"成功率: {summary.success_rate:.1f}%")
```

### 3. クラスベースの詳細制御

```python
import parallel_runner

def custom_function(user_id, api_key):
    """引数を受け取る関数の例"""
    # API呼び出しなどの処理
    time.sleep(0.1)  # 処理時間をシミュレート
    return {"user_id": user_id, "status": "success"}

# ParallelRunnerクラスで詳細制御
runner = parallel_runner.ParallelRunner(verbose=True)

# 分散実行
summary = runner.distribute(
    duration="30m",
    count=100,
    target_function=custom_function,
    max_workers=20,
    function_args=("user123",),          # 位置引数
    function_kwargs={"api_key": "key456"} # キーワード引数
)

# バースト実行
summary = runner.burst(
    count=50,
    target_function=custom_function,
    max_workers=15,
    function_args=("user456",),
    function_kwargs={"api_key": "key789"}
)

# 結果の詳細分析
for result in summary.results:
    if not result.success:
        print(f"エラー: {result.error_message}")
```

### 4. 段階的実行 - `progressive()`

複数のステージで段階的に実行します。

```python
import parallel_runner

def simple_task():
    time.sleep(0.05)  # 50ms の処理をシミュレート
    return "success"

# ステージ定義: (実行回数, 実行時間)
stages = [
    (20, "30s"),   # ウォームアップ: 20回/30秒
    (50, "30s"),   # 標準負荷: 50回/30秒  
    (100, "30s"),  # ピーク負荷: 100回/30秒
]

summaries = parallel_runner.progressive(
    stages=stages,
    target_function=simple_task,
    stage_interval=3.0  # ステージ間3秒待機
)

# 各ステージの結果を確認
for i, summary in enumerate(summaries, 1):
    print(f"ステージ{i}: 成功率 {summary.success_rate:.1f}%, RPS {summary.requests_per_second:.2f}")
```

### 5. Web API テストの実例

```python
import parallel_runner
import requests
import json

def test_api_endpoint(base_url, endpoint, method="GET", payload=None):
    """汎用API テスト関数"""
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

# API負荷テスト実行 - 1時間に200回
summary = parallel_runner.distribute(
    duration="1h",
    count=200,
    target_function=test_api_endpoint,
    max_workers=25,
    function_args=("https://jsonplaceholder.typicode.com", "posts/1"),
    function_kwargs={"method": "GET"}
)

print(f"API テスト完了:")
print(f"- 総実行数: {summary.total_requests}")
print(f"- 成功: {summary.successful_requests} ({summary.success_rate:.1f}%)")
print(f"- 平均レスポンス時間: {summary.average_response_time:.3f}秒")
print(f"- RPS: {summary.requests_per_second:.2f}")
```

### 6. データベースアクセステスト

```python
import parallel_runner
import sqlite3
import threading

# スレッドローカルストレージでDB接続を管理
thread_local = threading.local()

def get_db_connection():
    """スレッドごとにDB接続を取得"""
    if not hasattr(thread_local, 'connection'):
        thread_local.connection = sqlite3.connect('test.db')
    return thread_local.connection

def database_operation(query, params=None):
    """データベース操作をテスト"""
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

# データベース負荷テスト - 5分間に500回
summary = parallel_runner.distribute(
    duration="5m",
    count=500,
    target_function=database_operation,
    max_workers=10,
    function_args=("SELECT * FROM users WHERE id = ?",),
    function_kwargs={"params": (1,)}
)
```

## 時間指定フォーマット

時間は以下のフォーマットで指定できます：

- `"1h"` - 1時間
- `"30m"` - 30分  
- `"45s"` - 45秒
- `"2.5h"` - 2時間30分
- `"90m"` - 90分（1時間30分）

## API リファレンス

### 関数レベル API

```python
# 分散実行
parallel_runner.distribute(duration, count, target_function, **options)

# バースト実行  
parallel_runner.burst(count, target_function, **options)

# 段階的実行
parallel_runner.progressive(stages, target_function, **options)
```

### クラスベース API

```python
runner = parallel_runner.ParallelRunner(verbose=True)

# 分散実行
runner.distribute(duration, count, target_function, **options)

# バースト実行
runner.burst(count, target_function, **options)
```

### ExecutionConfig
実行設定を定義します。

- `total_requests`: 実行する総数
- `duration_hours`: 実行時間（時間単位）
- `max_workers`: 最大並列実行数

### ExecutionResult
個々の実行結果を格納します。

- `task_id`: タスクID
- `success`: 成功/失敗
- `duration`: 実行時間
- `response_data`: レスポンスデータ
- `error_message`: エラーメッセージ
- `timestamp`: 実行時刻

### ExecutionSummary
実行全体の結果サマリーです。

- `total_requests`: 総実行数
- `successful_requests`: 成功実行数
- `failed_requests`: 失敗実行数
- `total_duration`: 総実行時間
- `average_response_time`: 平均レスポンス時間
- `requests_per_second`: 秒間実行数
- `success_rate`: 成功率（%）
- `results`: 個別結果のリスト

## パッケージの構成

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

## 開発

### 開発環境のセットアップ

```bash
git clone https://github.com/sogatat/parallel-runner.git
cd parallel-runner
pip install -e ".[dev]"
```

### テスト実行

```bash
pytest tests/
```

### コードフォーマット

```bash
black parallel_runner/
flake8 parallel_runner/
```

## ライセンス

MIT License

## 作者
**Tasuya-SOGA**  
📧 sogatat@gmail.com  
🐙 [GitHub](https://github.com/sogatat)

**Masaki Yamamoto**  
📧 masaki.yamamoto373@gmail.com


## 貢献

プルリクエストやイシューを歓迎します。

## サポート

このライブラリが役に立った場合は、以下をご検討ください：
- ⭐ リポジトリにスターを付ける
- 🐛 GitHub Issues でバグ報告
- 💡 新機能の提案
- 📖 ドキュメントの改善

## 言語

- [English](README.md)
- [日本語](README-ja.md) (現在)