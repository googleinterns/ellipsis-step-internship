import setuptools 

setuptools.setup(
    name="recognition-pipeline-OFRI-AVIELI",
    version="0.0.1",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    # install_requires=['firebase-admin', 'apache-beam', 'google-cloud-vision']
)

