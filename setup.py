from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="silentstudio",
    version="0.3.1",
    author="SilentStudio",
    author_email="SilentStudio@Home.email.cn",
    description="SilentStudio CLI - 让开发者体验更好一点",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Silent-Studio-CN/SilentStudioCLI",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "colorama>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "silentstudio=silentstudio.cli:main",
            "ss=silentstudio.cli:main",
        ],
    },
)