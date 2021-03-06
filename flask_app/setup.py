"""
  Copyright 2020 Google LLC
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  Sets up the packages required for cloud dataflow pipeline imports.
"""
import setuptools

setuptools.setup(
    name="backend-pipelines",
    version="0.0.1",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'apache-beam==2.24.0',
        'firebase-admin==4.4.0',
        'flickrapi==2.4.0',
        'geohash2==1.1',
        'google-apitools==0.5.31',
        'google-cloud-vision==2.0.0',
        'Flask==1.1.2'
    ]
)
