# 1. パッケージビルド
python setup.py sdist bdist_wheel

# 2. ビルド成果物確認
ls dist/
# 期待される出力:
# parallel_runner-0.1.0-py3-none-any.whl
# parallel_runner-0.1.0.tar.gz

# 3. TestPyPIでテスト公開 (推奨)
pip install twine  # もしまだインストールしていなければ
twine upload --repository testpypi dist/*

# 4. TestPyPIからインストールテスト
pip install --index-url https://test.pypi.org/simple/ parallel-runner

# 5. 本番PyPIに公開
twine upload dist/*
