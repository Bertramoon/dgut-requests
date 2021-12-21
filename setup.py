#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Bertramoon
# Mail: bertramoon@126.com
# Created Date:  2021-3-26
# Modified Date:  2021-12-21
#############################################


from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dgut_requests",
    version="1.0",
    author="Bertramoon",
    author_email="bertramoon@126.com",
    description="用requests等库封装的东莞理工学院相关系统的爬虫脚本库，亦是东莞理工学院第一个pypi的爬虫库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BertraMoon/dgut-requests",
    project_urls={
        "Bug Tracker": "https://github.com/BertraMoon/dgut-requests/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=["requests==2.25.1", "lxml==4.6.3"]
)
