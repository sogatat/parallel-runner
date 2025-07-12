from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="parallel-runner",
    version="0.1.0",
    author="Tatsuya-SOGA",
    author_email="sogatat@gmail.com",
    description="A simple and flexible library for running parallel execution flows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sogatat/parallel-runner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Distributed Computing",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.7",
    install_requires=[
        # 標準ライブラリのみ使用するため、外部依存なし
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "requests": [
            "requests>=2.25.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # 必要に応じてCLIツールを追加
        ],
    },
    keywords="parallel execution, task flow, concurrent programming, distributed execution",
    project_urls={
        "Bug Reports": "https://github.com/sogatat/parallel-runner/issues",
        "Source": "https://github.com/sogatat/parallel-runner",
        "Documentation": "https://github.com/sogatat/parallel-runner/blob/main/README.md",
    },
)