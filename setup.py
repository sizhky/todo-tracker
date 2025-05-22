from setuptools import setup, find_packages


def readversion(filename):
    with open(filename, "r") as f:
        return f.read().strip()


setup(
    name="td",
    version=readversion("src/td/version"),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["typer", "torch-snippets", "pandas", "pydantic"],
    entry_points={
        "console_scripts": [
            "td=td:cli",
            "tdx-old=td:_cli",
            "tdx=td.ui.textual.v2.app:main",
        ],
    },
    python_requires=">=3.8",
    author="Yeshwanth",
    description="A command-line todo tracker application",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
