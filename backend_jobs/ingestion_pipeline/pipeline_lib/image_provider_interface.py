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
 # pylint: disable=pointless-string-statement

from abc import ABC, abstractmethod
import apache_beam as beam

""" Each ImageProvider that is added to the platform will inherit from the ImageProviders class.
This class is in charge of:
* returning images from the provider.
* calculating the number of batches we want to run in parallel.
* extracting additional metadata.
"""

class ImageProvider(ABC, beam.DoFn):
    """ ImageProvider is an interface that all the image ingestion providers inherit from.
    """

    @abstractmethod
    def get_images(self, num_of_page, query_arguments):
        """ This function is in charge of calling an API/Image provider source
        and returns a list of images.

        Args:
            num_of_batches: the number of the batches we want to run in parallel.
            num_of_images: the amount of images we retrieve.
            query_arguments: a map object contaning arguments we retrieve images by.

        Returns:
            list of images with info on the images.
        """

    @abstractmethod
    def get_num_of_pages(self, query_arguments):
        """ This function is in charge of calculating the amount of pages we want to retrieve.

        Args:
            query_arguments: a map object contaning arguments we retrieve images by.

        Returns:
            num_of_batches: number
        """

    @abstractmethod
    def get_image_attributes(self, element):
        """ This function is in charge of extracting the metadata from each image.

        Args:
            element: the image we get from the get_images function.

        Returns:
            imageAttributes: An ImageAttributes class that contains all the information on the image.
        """

    @abstractmethod
    def get_url_for_max_resolution(self, resolution, image_id):
        """ This function gets a resolution and an image_id, and generates a new url
        with the closest below fit required resolution.

        Args:
            resolution: A dict representing closest height and width.
            For example {'height': 480, 'width': 640}
            image_id: str in the format providername + number

        Returns:
            url: A url referring to the image with the closest fit resolution.
        """

    def _genarate_image_id_with_prefix(self, image_id):
        """ This function gets a image_id and and adds a unique provider prefix.

        Args:
            image_id: The unique id the provider provides.

        Returns:
            new_image_id: Unique id with provider id as prefix.
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
    def image_type(self):
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
