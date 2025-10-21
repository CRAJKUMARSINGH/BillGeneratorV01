from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bill-generator",
    version="1.0.0",
    author="Rajkumar Singh",
    author_email="crs25071988@gmail.com",
    description="Professional Infrastructure Billing System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CRAJKUMARSINGH/BillGeneratorV01",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={},
)