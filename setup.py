import setuptools
 
setuptools.setup(
    name="aiwolf",
    version="0.9.1",
    author="OTSUKI Takashi",
    author_email="aiwolfsharp@outlook.com",
    description="The package for creating AIWolf agent in Python",
    long_description="This is a Python port of AIWolfLib, a .NET package.",
    long_description_content_type="text/markdown",
    url="https://github.com/AIWolfSharp/aiwolf-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache-2.0",
        "Operating System :: OS Independent",
    ]
)