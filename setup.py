from setuptools import setup

setup(
    name="balecore",
    version="1.0.8",
    entry_points={
        "console_scripts": [
            "balecore = balecore.__main__:main"
        ]
    }
)