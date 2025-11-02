from setuptools import setup, find_packages

setup(
    name="personaops",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "pydantic>=2",
        "jinja2",
        "typer[all]",
        "requests",
        "python-dotenv",
        "jsonschema",
        "openai>=1.46.0"
    ],
    entry_points={
        "console_scripts": [
            "personaops=src.cli.app:app",
        ],
    },
)