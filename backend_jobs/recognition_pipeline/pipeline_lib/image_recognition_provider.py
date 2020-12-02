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

from abc import ABC, abstractmethod
import apache_beam as beam
from backend_jobs.recognition_pipeline.filters import filter_by_format, filter_by_resolution
from backend_jobs.ingestion_pipeline.providers.providers import\
  get_provider, IMAGE_PROVIDERS
from backend_jobs.pipeline_utils import database_schema
from backend_jobs.recognition_pipeline.pipeline_lib import constants


class ImageRecognitionProvider(ABC, beam.DoFn):
    """ Each recognition provider used in our project
    will have an implementation of this abstract class.

    All recognition providers need to have a method for labeling the images,
    an Id property and the latest version.

    """
    @abstractmethod
    def process(self, element):
        """Labels a batch of images from dataset using a specific recognition provider.

        Args:
            element: a list of images information dictionaries.
            Each Python dictionary contains all of the images' fields and their
            values as stored in the database.

        Returns:
            list of lists in which each inner list is a tuple of a image dictionary
            and all labels recognized in it by the provider.
            For example: [[({url:string, imageAttributes:map, etc.},
            ['dog', 'fur])], [(another image's dictionary, ['cat', 'fur'])]]

        """

    def is_eligible(self, image):
        """ Checks if the image is eligible for being labeled by the provider.

        For each criteria of the providers requirements - resolution and filter,
        checks if the image's attributes match the providers prerequisites.

        Args:
            image: a dictionary if all image's Firebase document's fields.
            Each dictionary contains all of the images' fields and their
            values as stored in the database_schema.COLLECTION_IMAGES.
  
        Returns:
            True iff the image's attributes meet the provider's prerequisites
            and the image can be labeled by the provider

        """
        resolution_filter = filter_by_resolution.FilterByResolution(self._resolution_prerequisites)
        format_filter = filter_by_format.FilterByFormat(self._format_prerequisites)
        return resolution_filter.is_supported(image) and format_filter.is_supported(image)

    def _change_url_by_resolution(self, image):
        """ Adds an image's url field to match the supported resolution.

            Iterates through all image providers and checks if
            the image can be resized to a supported resolution.
            If it can, adds a field of an image url which contains
            an image of the supported resolution.

        """
        for provider_name in image[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS]:
            provider = get_provider(IMAGE_PROVIDERS, provider_name)
            resize_url = provider.get_url_for_min_resolution(\
                self._resolution_prerequisites['height'],\
                    self._resolution_prerequisites['width'], image)
            if resize_url:
                image[constants.FIELD_URL_FOR_RECOGNITION_API] =\
                    resize_url
                return image
            return image

    def add_url_for_recognition_api(self, image):
        """ Adds a URL_FOR_RECOGNITION_API field with the url in the supported
            resolution if possible.

            If the image is in the supported resolution, copies the url to the
            a new URL_FOR_RECOGNITION_API field. Otherwise - checks if it can be
            resized to the correct resolution.
            If the image cannot be supported - the dictionary remains without
            the new field.

        """
        image_attribute = image[database_schema.COLLECTION_IMAGES_FIELD_IMAGE_ATTRIBUTES]\
            [database_schema.COLLECTION_IMAGES_FIELD_RESOLUTION]
        min_height = self._resolution_prerequisites['height']
        min_width = self._resolution_prerequisites['width']
        if image_attribute['width'] >= min_width and \
            image_attribute['height'] >= min_height:
            # current url is in a supported resolution
            image[constants.FIELD_URL_FOR_RECOGNITION_API] =\
                image[database_schema.COLLECTION_IMAGES_FIELD_URL]
            return [image]
        return [self._change_url_by_resolution(image)]

    @property
    def _resolution_prerequisites(self):
        """ A dictionary of the resolution supported by the provider.
        for example: {'width': 680, 'height': 480}

        """
        raise NotImplementedError

    @property
    def _format_prerequisites(self):
        """ A list of all image formats supported by the provider.
        for example: ['JPG', 'PNG']

        """
        raise NotImplementedError

    @property
    def provider_id(self):
        """ A string of the image recognition provider's id.

        """
        raise NotImplementedError

    @property
    def provider_version(self):
        """ A string of the image recognition provider's version.

        """
        raise NotImplementedError
    