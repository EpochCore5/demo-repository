from setuptools import setup, find_packages

setup(
    name='epochcore',
    version='4.0.0',
    packages=find_packages(),
    description='EpochCore Agent System for Recursive Autonomous Operations',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'epochcore=epochcore.cli:main',
        ],
    },
)
