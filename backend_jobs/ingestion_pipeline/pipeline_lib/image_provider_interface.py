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


Each ImageProvider that is added to the platform will inherit from the ImageProviders class.
This class is in charge of:
* Returning images from the provider.
* Calculating the number of batches we want to run in parallel.
* Extracting additional metadata.
"""

from abc import ABC, abstractmethod
import apache_beam


class ImageProvider(ABC, apache_beam.DoFn):
    """ ImageProvider is an interface that all the image ingestion providers inherit from.
    """

    @abstractmethod
    def get_images(self, page_number):
        """ This function is in charge of calling an API/Image provider source
        and returns a iterable collection of images.

        Args:
            page_number: The page number at which to start image retrieval.

        Returns:
            Iterable collections of objects, provider specifics.
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
            element: An object the provider provides, provider specific.

        Returns:
            imageAttributes: An ImageAttributes class that contains all the information
            on the image.
        """

    @abstractmethod
    def get_url_for_min_resolution(self, min_height, min_width, image):
        """ This function gets a resolution and an image.
        This function generates a new url with the closest above fit required resolution,
        if there is no above fit raises an error.

        Args:
            min_height: Int representing closest min height to retrieve.
            min_width: Int representing closest min width to retrieve.
            image: A dict contaning all the fields of the image in the database

        Returns:
            url: A url referring to the image with the closest above fit resolution.
        """

    @property
    def provider_id(self):
        """ A unique id of the provider, e.g. FlickrProvider_2020. """
        raise NotImplementedError

    @property
    def provider_version(self):
        """ The version of the provider. """
        raise NotImplementedError

    @property
    def enabled(self):
        """ Whether we can ingest images from this provider. """
        raise NotImplementedError

    @property
    def visibility(self):
        """ Type VisibilityType - The provider visibility. """
        raise NotImplementedError
