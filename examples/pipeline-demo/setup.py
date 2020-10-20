import setuptools 

setuptools.setup(
    name="ImageRecognitionPipeline",
    version="1.0",
    install_requires=[
        "google-cloud-vision",
        "firebase-admin",
        "apache-beam"
    ],
    packages=setuptools.find_packages(),
    data_files=[('additional_files_dir', ['additional_files_dir/interface.py'])],
    include_package_data=True,
)
