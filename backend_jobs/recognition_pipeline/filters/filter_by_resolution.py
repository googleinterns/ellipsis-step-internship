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

from backend_jobs.recognition_pipeline.pipeline_lib.filter_by import FilterBy
from backend_jobs.ingestion_pipeline.providers.providers import\
  get_provider, IMAGE_PROVIDERS
from backend_jobs.pipeline_utils import database_schema
from backend_jobs.recognition_pipeline.pipeline_lib import constants

class FilterByResolution(FilterBy):
    """ Checks if the image has a high enough resolution.

    """

    def is_supported(self, image):
        """ Returns True iff image resolution is equal or bigger
            than the minimum supported resolution supported by the provider.
            The image is supported only if a URL_FOR_RECOGNITION_API field
            exists in the image doc.

            Args:
              image: A dictionary representing the image's doc.
              Each image is represented by a Python dictionary containing all the fields
              of the document in the database_schema.COLLECTION_IMAGES
              and their values.

        """
        return constants.FIELD_URL_FOR_RECOGNITION_API in image

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
              self.prerequisites['height'], self.prerequisites['width'], image)
            if resize_url:
                image[constants.FIELD_URL_FOR_RECOGNITION_API] =\
                  resize_url
                return

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
        min_height = self.prerequisites['height']
        min_width = self.prerequisites['width']
        if image_attribute['width'] >= min_width and \
          image_attribute['height'] >= min_height:
            # current url is in a supported resolution
            image[constants.FIELD_URL_FOR_RECOGNITION_API] =\
              image[database_schema.COLLECTION_IMAGES_FIELD_URL]
        else:
            self._change_url_by_resolution(image)
