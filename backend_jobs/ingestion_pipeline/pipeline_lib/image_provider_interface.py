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
import apache_beam

""" Each ImageProvider that is added to the platform will inherit from the ImageProviders class.
This class is in charge of:
* Returning images from the provider.
* Calculating the number of batches we want to run in parallel.
* Extracting additional metadata.
"""

class ImageProvider(ABC, apache_beam.DoFn):
    """ ImageProvider is an interface that all the image ingestion providers inherit from.
    """
    @abstractmethod
    def __init__(self, query_arguments):
        """ This function is in charge of calling an API/Image provider source
        and returns a iterable collection of images.

        Args:
            num_of_page: The number of page we want to retrieve images from.
        """

    @abstractmethod
    def get_images(self, num_of_page):
        """ This function is in charge of calling an API/Image provider source
        and returns a iterable collection of images.

        Args:
            num_of_page: The number of page we want to retrieve images from.

        Returns:
            Iterable collections of objects, can be different between providers.
        """

    @abstractmethod
    def get_num_of_pages(self):
        """ This function is in charge of calculating the amount of pages we want to retrieve.

        Returns:
            Number of pages.
        """

    @abstractmethod
    def get_image_attributes(self, element):
        """ This function is in charge of extracting the metadata from each image.

        Args:
            element: An object the provider provides, can be a different between providers.

        Returns:
            imageAttributes:An ImageAttributes class that contains all the information on the image.
        """

    @abstractmethod
    def get_url_for_max_resolution(self, resolution, image):
        """ This function gets a resolution and an image.
        This function generates a new url with the closest below fit required resolution.

        Args:
            resolution: A dict representing closest height and width.
            For example {'height': 480, 'width': 640}
            image: A dict contaning all the fields of the image in the database

        Returns:
            url: A url referring to the image with the closest below fit resolution.
        """

    @abstractmethod
    def _genarate_image_id_with_prefix(self, image_id):
        """ This function gets a image_id and adds a unique provider prefix.

        Args:
            image_id: The unique image id the provider provides the image.

        Returns:
            new_image_id: Unique id with provider id as prefix.
        """

    @property
    def provider_id(self):
        """ A unique id of the provider, e.g. FlickrProvider_2020. """
        raise NotImplementedError
    @property
    def provider_name(self):
        """ A friendly name of the provider, e.g. FlickrProvider. """
        raise NotImplementedError
    @property
    def provider_version(self):
        """ The version of the provider. """
        raise NotImplementedError
    @property
    def image_type(self):
        """ The type of images the provider provides, e.g. Drone. """
        raise NotImplementedError
    @property
    def enabled(self):
        """ Whether we can ingest images from this provider. """
        raise NotImplementedError
    @property
    def visibility(self):
        """ The visibility type of images provided by this image provider. """
        raise NotImplementedError
    @property
    def num_of_images(self):
        """ The number of images we receive in every batch of get_images. """
        raise NotImplementedError
    @property
    def query_arguments(self):
        """ A dict that represents the args we query by, e.g.: {'tag':'cat', 'date':'12/3/2020'} """
        raise NotImplementedError
