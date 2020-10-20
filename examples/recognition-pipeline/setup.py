import setuptools 

PACKAGE_NAME = 'my_package'
PACKAGE_VERSION = '0.0.1'

setuptools.setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    install_requires=[
        "google-cloud-vision",
        "firebase-admin",
        "apache-beam"
    ],
    packages=setuptools.find_packages(),
    package_data= {
        PACKAGE_NAME: [
            "additional_files_dir/*.py"
        ],
    },
)
    
    # data_files=[('additional_files_dir', ['additional_files_dir/interface.py'])],
    # include_package_data=True,
# )
