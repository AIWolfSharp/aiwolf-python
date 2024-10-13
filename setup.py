import setuptools

setuptools.setup(
    name="aiwolf",
    version="1.3.0",
    author="OTSUKI Takashi",
    author_email="aiwolfsharp@outlook.com",
    url="https://github.com/AIWolfSharp/aiwolf-python",
    description="The package for creating AIWolf agent in Python",
    #    long_description="This is a Python port of AIWolfLib, a .NET package.",
    long_description_content_type="text/markdown",
    license="Apache Software License",
    packages=setuptools.find_packages(),
    package_data={
        "aiwolf": ["py.typed"],
    },
    classifiers=[  # see https://pypi.org/pypi?:action=list_classifiers
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8"
    ],
)
