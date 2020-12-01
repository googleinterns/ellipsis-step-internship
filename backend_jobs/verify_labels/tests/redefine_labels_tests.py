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
from backend_jobs.verify_labels.pipeline_lib.redefine_labels import RedefineLabels, get_redefine_map

class TestRedefineLables(unittest.TestCase):
    """ Tests FilterBy interface implementations.

    """

    def setUp(self):
        self.cat_image = {'url':'https://live.staticflickr.com/3677/13545844805_170ec3746b_c.jpg',\
            'imageAttributes':{'format': 'jpg', 'resolution': {'width': 800, 'height': 600}},\
                'ingestedProviders': [], 'labelName': 'cat'}
        self.cats_image = {'url':'https://live.staticflickr.com/3677/13545844805_170ec3746b_c.jpg',\
            'imageAttributes':{'format': 'jpg', 'resolution': {'width': 800, 'height': 600}},\
                'ingestedProviders': [], 'labelName': 'cats'}
        self.dog_image =  {'url':'https://live.staticflickr.com/5284/5338762379_59f7435b93_c.jpg',\
            'imageAttributes': {'format': 'pdf', 'resolution': {'width': 800, 'height': 600}},\
                'ingestedProviders': [], 'labelName': 'dog'}
        provider_id = 'For_Tests' # A document in the Firestore database designated for tests.
        self.redefine_map = get_redefine_map(provider_id)

    def test_redefine_known_labels(self):
        """ Tests for redefining labels that are known to the project's database.

        both 'cat' and 'cats' labels are known and mapped to id_for_cat.

        """
        returned_image, redefined_labels = RedefineLabels().process(\
            self.cat_image, self.redefine_map).__next__()
        # Checks that the image dict returned is the same as the dict sent.
        self.assertEqual(returned_image, self.cat_image)
        # Checks that label was redefined to 'id_for_cat'.
        self.assertTrue('id_for_cat' in redefined_labels)
        returned_image, redefined_labels = RedefineLabels().process(\
            self.cats_image, self.redefine_map).__next__()
        # Checks that the image dict returned is the same as the dict sent.
        self.assertEqual(returned_image, self.cats_image)
        # Checks that label was redefined to 'id_for_cat'.
        self.assertTrue('id_for_cat' in redefined_labels)


    def test_redefine_unknown_labels(self):
        """ Tests for redefining labels that are unknown to the project's database.

        'dog' label is not known to the system and therefore doesn't map to any id.
        The label doc has no value for the rest of the pipeline, and therefore is
        not returned.

        """
        returned_generator = RedefineLabels().process(\
            self.dog_image, self.redefine_map)
        # Checks that returned-generator is empty - no redefined label ids.
        self.assertRaises(StopIteration, returned_generator.__next__)

if __name__ == '__main__':
    unittest.main()
