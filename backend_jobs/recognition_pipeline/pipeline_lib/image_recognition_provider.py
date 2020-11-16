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

class ImageRecognitionProvider(ABC, beam.DoFn):
    """ Each recognition provider used in our project
    will have an implementation of this abstract class.

    All recognition providers need to have a method for labeling the images,
    an Id property and the latest version.
    """
    @abstractmethod
    def label_images(self, element):
        """Labels a batch of images from dataset using a specific recognition provider.

        Args:
            element: a list of images information dictionaries.

        Returns:
            list of lists in which each inner list is a tuple of a image dictionary
            and all labels recognized in it by the provider.
            For example: [[({url:string, imageAttributes:map, etc.},
            ['dog', 'fur])], [(another image's dictionary, ['cat', 'fur'])]]
        """

    def is_eligible(self, image):
        """ Checks if the image is eligible for being labeled by the provider.

        For each criteria of the providers requirements,
        checks if the image's attributes match the providers prerequisites.

        Args:
            image: a dictionary if all image's Firebase document's fields.
            One of them being 'imageAttributes' which is a map of
            all the image's attributes and their values.
        """
        for criteria, criteria_filter in self.prerequisites_map.items():
            if criteria not in image['imageAttributes'] or \
                not criteria_filter.is_supported(image):
                # If the image doesn't have this property stored or
                # the property doesn't meet the perequisites then it is not supported.
                return False
        # All checks passed, the image can be labeled by the provider.
        return True

    @property
    def prerequisites_map(self):
        """ A map of an attribute criteria and a FilterBy object
        that filters by the corresponding attribute.
        For example: {'Format':FilterByFormat(['JPG'])}.
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
    