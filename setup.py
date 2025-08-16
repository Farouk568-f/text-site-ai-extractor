from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="text-site-ai-extractor",
    version="1.0.0",
    author="Farouk568-f",
    author_email="",
    description="Advanced Arabic text extraction API with intelligent duplicate removal and content filtering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Farouk568-f/text-site-ai-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "text-extractor=article_api:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "text-extraction",
        "arabic-text",
        "web-scraping",
        "content-filtering",
        "duplicate-removal",
        "api",
        "flask",
        "beautifulsoup",
        "nlp",
        "text-processing",
    ],
    project_urls={
        "Bug Reports": "https://github.com/Farouk568-f/text-site-ai-extractor/issues",
        "Source": "https://github.com/Farouk568-f/text-site-ai-extractor",
        "Documentation": "https://github.com/Farouk568-f/text-site-ai-extractor#readme",
    },
)
