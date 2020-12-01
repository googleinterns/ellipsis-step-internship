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
from backend_jobs.recognition_removal.pipeline_lib.firestore_database import union

class TestUnionMethod(unittest.TestCase):
    """ Tests union method.

    """
    def setUp(self):
        self.list_of_lists = [[1], [2], [1, 2], []]

    def test_union_method(self):
        """ Tests that the union method works as it should.
        Returns a list of all distinct elements in list_of_lists.

        """
        expected_result = [1, 2]
        self.assertEqual(union(self.list_of_lists), expected_result)

if __name__ == '__main__':
    unittest.main()
