import setuptools 

setuptools.setup(
    name="recognition-pipeline-OFRI-AVIELI",
    version="0.0.1",
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",
    packages=setuptools.find_packages(include=['recognition-pipeline', 'recognition-pipeline.*','recognition-pipeline.additional_files_dir', 'recognition-pipeline.additional_files_dir.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['firebase-admin', 'apache-beam', 'google-cloud-vision']
)

