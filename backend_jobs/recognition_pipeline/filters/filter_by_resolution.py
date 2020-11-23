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
from backend_jobs.pipeline_utils.utils import get_provider
from backend_jobs.ingestion_pipeline.main import IMAGE_PROVIDERS
from backend_jobs.pipeline_utils import database_schema

class FilterByResolution(FilterBy):
    """ Checks if the image has a high enough resolution.

    """

    def is_supported(self, image):
        """ Returns True iff image resolution is equal or bigger
            than the minimum supported resolution supported by the provider.

            Args:
              image: A dictionary representing the image's doc.
              Each image is represented by a Python dictionary containing all the fields
              of the document in the database and their values.

        """
        image_attribute = image[database_schema.COLLECTION_IMAGES_FIELD_IMAGE_ATTRIBUTES]\
          [database_schema.COLLECTION_IMAGES_FIELD_RESOLUTION]
        min_height = self.prerequisites['height']
        min_width = self.prerequisites['width']
        if image_attribute['width'] >= min_width and \
          image_attribute['height'] >= min_height:
            return True
        return self._change_url_by_resolution(image)

    def _change_url_by_resolution(self, image):
        """ Returns True iff the image's url was changed to a supported resolution

          Iterates through all image providers and checks if
          the image can be resized to a supported resolution.
          If it can, changes the image url in the image
          dictionary to be the correct one and returns True.
          Otherwise, the image cannot be supported and returns False.

      """
        for provider_name in image[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS]:
            provider = get_provider(IMAGE_PROVIDERS, provider_name)
            resize_url = provider.get_url_for_max_resolution(self.prerequisites, image)
            if resize_url:
                image[database_schema.COLLECTION_IMAGES_FIELD_URL] = resize_url
                return True
        return False
