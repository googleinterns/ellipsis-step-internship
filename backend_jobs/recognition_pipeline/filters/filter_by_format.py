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

class FilterByFormat(FilterBy):
    """ Checks if the image is in a correct format.

    """

    def is_supported(self, image):
        """ Returns True iff image's format is in list of allowed formats.

        """
        image_attribute = image['imageAttributes']['format']
        return image_attribute.upper() in self.prerequisites
 