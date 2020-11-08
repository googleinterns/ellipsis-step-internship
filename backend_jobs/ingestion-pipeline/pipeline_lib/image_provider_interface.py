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
 """

from abc import ABC
import apache_beam as beam

"""
Each image provider that is added to the platform will inherit from the ImageProviders class.
This class is incharge of:
* returning images from the provider
* calculting the num of baches we want to run in parallel
* extarcting additional metadata.
"""

class ImageProvider(ABC, beam.DoFn):

    def get_images(self, num_of_batches, num_of_images, query_arguments):
        """
        This function is incharge of callind an API/Image provider source
        and receives a list of images
        Args:
            num_of_batches: the number of the batches we want to run in parallel
            num_of_images: the amount of images we retrieve
            query_arguments: a map object contaning arguments we retrieve images by
        Returns:
            list of images with info on the images.
        """

    def get_num_of_batches(self, query_arguments):
        """
        This function is incharge of calculating the amount of batches we want to call
        Args:
            query_arguments: a map object contaning arguments we retrieve batches by
        Returns:
            num_of_batches: number
        """

    def get_image_attributes(self, element):
        """
        This function is incharge of exracting the metadata from each image
        Returns:
            imageAttributes: ImageAttributes- a class that contains all the info on the image
        """

    def get_url_by_resolution(self, resolution, image_id):
        """
        This function gets a resolution and an image_id, and generates a new url
        with the required resolution
        Returns:
            url: a url reffering to the image in the requested resolution
        """

    # pylint: disable=missing-function-docstring
    @property
    def provider_id(self):
        raise NotImplementedError
    @property
    def provider_name(self):
        raise NotImplementedError
    @property
    def provider_version(self):
        raise NotImplementedError
    @property
    def provider_type(self):
        raise NotImplementedError
    @property
    def enabled(self):
        raise NotImplementedError
    @property
    def visibility(self):
        raise NotImplementedError
    @property
    def num_of_images(self):
        raise NotImplementedError
