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

import unittest
from backend_jobs.recognition_pipeline.filters.filter_by_format import FilterByFormat
from backend_jobs.recognition_pipeline.filters.filter_by_resolution import FilterByResolution

class TestFilterBy(unittest.TestCase):
    """ Tests FilterBy interface implementations.

    """
    def setUp(self):
        self.supported_image = {'imageAttributes' : {'format': 'jpg', 'resolution':\
            {'width': 800, 'height': 600}}, 'ingestedProviders': []}
        self.unsupported_image =  {'imageAttributes' : {'format': 'pdf', 'resolution':\
            {'width': 600, 'height': 400}}, 'ingestedProviders': []}
        format_filter = FilterByFormat(['JPG'])
        resolution_filter = FilterByResolution({'width': 640, 'height': 480})
        self.filters = [format_filter, resolution_filter]

    def test_filters(self):
        """ Tests both supported and unsupported images by all filters.
        All filters in self.filters should support the supported image
        and not support the unsupported image.

        """
        for filter_by in self.filters:
            self.assertTrue(filter_by.is_supported(self.supported_image))
            self.assertFalse(filter_by.is_supported(self.unsupported_image))

if __name__ == '__main__':
    unittest.main()
