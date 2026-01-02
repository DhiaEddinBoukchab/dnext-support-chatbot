from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dnext-support-chatbot",
    version="1.0.0",
    author="Dhia BOUKCHAB",
    author_email="dhia.boukchab@dnext.io",
    description="RAG-based customer support chatbot for Dnext platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dnext-support-chatbot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "gradio>=4.0.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
        "groq>=0.4.0",
        "python-dotenv>=1.0.0",
    ],
)
