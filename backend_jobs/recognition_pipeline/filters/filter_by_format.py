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
from backend_jobs.pipeline_utils import database_schema

class FilterByFormat(FilterBy):
    """ Checks if the image is in a correct format.

    """

    def is_supported(self, image):
        """ Returns True iff image's format is in list of allowed formats.

          Args:
              image: A dictionary representing the image's doc.
              Each image is represented by a Python dictionary containing all the fields
              of the document in the database and their values.

        """
        image_attribute = image[database_schema.IMAGE_ATTRIBUTES][database_schema.FORMAT]
        return image_attribute.upper() in self.prerequisites
 