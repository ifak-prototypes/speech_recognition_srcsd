# -*- coding: utf-8 -*-

# Copyright speech recognition server authors. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from setuptools import setup, find_packages
import codecs


README = codecs.open("README.md", encoding="utf-8").read()

setup(
    name="srcsd",
    version="1.0.0",
    description="Speech Recognition Client/Server and Desktop application (SRCSD)",
    long_description=README,
    author="ifak e.V. and Keanu-Farell Kunzi",
    license="MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Sound/Audio :: Speech"
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "devtools",
        "fastapi",
        "openai-whisper @ git+https://github.com/openai/whisper.git",
        "PyAudio",
        "pyautogui",
        "pydub",
        "pygments",
        "pykka",
        "pyperclip",
        "python-multipart",
        "requests",
        "SpeechRecognition==3.8.1",
        "uvicorn"
        ],
    extras_require={
        "dev": [
            "mypy",
            "types-requests"
        ]
    },
    python_requires=">=3.10"
)
