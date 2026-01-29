#!/usr/bin/env python3
"""
ClawdForDummies - Security Assessment Tool for Clawdbot/Moltbot

A user-friendly security scanner that helps non-technical users identify
vulnerabilities in their Clawdbot/Moltbot deployments.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Security assessment tool for Clawdbot/Moltbot deployments"

setup(
    name="clawd-for-dummies",
    version="1.0.0",
    author="ClawdForDummies Team",
    author_email="security@clawdfordummies.dev",
    description="Security assessment tool for Clawdbot/Moltbot deployments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/clawd-for-dummies",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psutil>=5.9.0",
        "requests>=2.28.0",
        "colorama>=0.4.6",
        "rich>=13.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "build": [
            "pyinstaller>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clawd-for-dummies=clawd_for_dummies.__main__:main",
            "cfd=clawd_for_dummies.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "clawd_for_dummies": [
            "templates/*.html",
            "templates/*.md",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/clawd-for-dummies/issues",
        "Source": "https://github.com/yourusername/clawd-for-dummies",
        "Documentation": "https://github.com/yourusername/clawd-for-dummies/blob/main/docs/USER_GUIDE.md",
    },
)
