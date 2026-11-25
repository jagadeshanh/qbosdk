from pathlib import Path

from setuptools import setup

setup(
    name="qbosdkonline",
    version="0.1.0",
    description="QuickBooks Online integration SDK",
    long_description=Path(__file__).with_name("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    license="MIT",
    license_files=["LICENSE"],
    url="https://github.com/jagadeshanh/qbosdk",
    project_urls={
        "Documentation": "https://qbosdk.readthedocs.io/en/latest/",
        "Issues": "https://github.com/jagadeshanh/qbosdk/issues",
    },
    packages=["qbosdk"],
    python_requires=">=3.9",
)
