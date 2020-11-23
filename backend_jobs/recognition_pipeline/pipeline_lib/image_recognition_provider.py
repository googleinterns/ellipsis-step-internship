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
from backend_jobs.recognition_pipeline.providers import google_vision_api

# Maps recognition provider names to an object of the provider.
NAME_TO_PROVIDER = {'Google_Vision_API': google_vision_api.GoogleVisionAPI}

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
            Each dictionary contains all of the images' fields and their
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
            values as stored in the database.
        
        Returns:
            True iff the image's attributes meet the provider's prerequisites
            and the image can be labeled by the provider

        """
        resolution_filter = filter_by_resolution.FilterByResolution(self._resolution_prerequisites)
        format_filter = filter_by_format.FilterByFormat(self._format_prerequisites)
        return resolution_filter.is_supported(image) and format_filter.is_supported(image)

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
    