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
    def get_images(self, num_of_page, query_arguments):
        """ This function is in charge of calling an API/Image provider source
        and returns a iterable collection of images.

        Args:
            num_of_batches: The number of the batches we want to run in parallel.
            num_of_images: The amount of images we retrieve.
            query_arguments: A map object contaning arguments we retrieve images by.

        Returns:
            The return type can be different iterable collections between providers.
        """

    @abstractmethod
    def get_num_of_pages(self, query_arguments):
        """ This function is in charge of calculating the amount of pages we want to retrieve.

        Args:
            query_arguments: A map object contaning arguments we retrieve images by.

        Returns:
            Number of pages.
        """

    @abstractmethod
    def get_image_attributes(self, element):
        """ This function is in charge of extracting the metadata from each image.

        Args:
            element: An image the provider provides, can be a different type between providers.

        Returns:
            imageAttributes:An ImageAttributes class that contains all the information on the image.
        """

    @abstractmethod
    def get_url_for_max_resolution(self, resolution, image_id):
        """ This function gets a resolution and an image_id, and generates a new url
        with the closest below fit required resolution.

        Args:
            resolution: A dict representing closest height and width.
            For example {'height': 480, 'width': 640}
            image_id: Image unique id.

        Returns:
            url: A url referring to the image with the closest below fit resolution.
        """

    @abstractmethod
    def parse_query_by_args(self, args):
        """ This function gets arguments and returns a dict with the args we query by.

        Args:
            args: A string that includes all the arg we will query by, e.g. "cat_12/3/2020".

        Returns:
            A dict that represents the args, e.g.: {'tag':'cat', 'date':'12/3/2020'}.
        """

    @abstractmethod
    def _genarate_image_id_with_prefix(self, image_id):
        """ This function gets a image_id and and adds a unique provider prefix.

        Args:
            image_id: The unique image id the provider provides the image.

        Returns:
            new_image_id: Unique id with provider id as prefix.
        """

    @property
    def provider_id(self):
        """ A unique id of the provider, e.g. FlickrProvider-2020.
        """
        raise NotImplementedError
    @property
    def provider_name(self):
        """ A friendly name of the provider, e.g. FlickrProvider.
        """
        raise NotImplementedError
    @property
    def provider_version(self):
        """ The version of the provider.
        """
        raise NotImplementedError
    @property
    def image_type(self):
        """ The type of images the provider provides, e.g. Drone.
        """
        raise NotImplementedError
    @property
    def enabled(self):
        """ Whether we can ingest images from this provider.
        """
        raise NotImplementedError
    @property
    def visibility(self):
        """ The visibility type of images provided by this image provider.
        """
        raise NotImplementedError
    @property
    def num_of_images(self):
        """ The number of images we receive in every batch of get_images.
        """
        raise NotImplementedError
