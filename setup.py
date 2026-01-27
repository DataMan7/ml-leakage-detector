"""
Setup configuration for ML Leakage Detector package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ml-leakage-detector",
    version="1.0.0",
    author="Dennis Ombonga Mong'are",
    author_email="m.oomboga@gmail.com",
    description="Automatic detection of data leakage in ML pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ml-leakage-detector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "scikit-learn>=1.3.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "astor>=0.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "pylint>=3.0.0",
            "jupyter>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ml-leakage-detector=src.detector:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
