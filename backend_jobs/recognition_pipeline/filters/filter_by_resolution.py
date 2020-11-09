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

from pipeline_lib.filter_by import FilterBy
# from ingestion-pipeline.main import get_image_provider TODO: add this after merging with Tal's branch

class FilterByResolution(FilterBy):
    """ Checks if the image has a high enough resolution.

    """

    def is_supported(self, image):
        """ Returns True iff image resolution is equal or bigger
            than the minimum supported resolution supported by the provider.

        """
        image_attribute = image['imageAttributes']['resolution']
        min_length = self.prerequisites['height']
        min_width = self.prerequisites['width']
        if image_attribute['width'] >= min_width and \
          image_attribute['height'] >= min_length:
            return True
        return self.change_url_by_resolution(image)

    def change_url_by_resolution(self, image):
        """ Returns True iff the image's url was changed to a supported resolution

          Iterates through all image providers and checks if
          the image can be resized to a supported resolution.
          If it can, changes the image url in the image
          dictionary to be the correct one and returns True.
          Otherwise, the image cannot be supported and returns False.
      """
        """ TODO: add this after merging with Tal's branch
        for provider_name in image['ingestedProviders']:
            provider = get_image_provider(provider_name)
            resize_url = provider.get_url_by_resolution(self.prerequisites)
            if resize_url:
              image['url'] = resize_url
              return True
      """
        return False
