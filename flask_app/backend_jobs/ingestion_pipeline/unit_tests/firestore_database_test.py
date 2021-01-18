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
import datetime
from backend_jobs.ingestion_pipeline.pipeline_lib import firestore_database
from backend_jobs.pipeline_utils import data_types


class TestFirestoreDatabase(unittest.TestCase):
    """ This class tests helper functions from the firebase_database class.
    """
  
    def test_get_geo_hashes_map1(self):
        """ This test, given values of latitude and longitude,
        expects to receive a map object with the value 'hash10' and key '9q8yvy60hd'.

        Given:
            latitude=37.783371, longitude=-122.439687

        Expects:
            {...'hash10': '9q8yvy60hd', ...}
        """
        expected_hashes_map = '9q8yvy60hd'
        hashes_map = firestore_database._get_geo_hashes_map(37.783371, -122.439687)
        self.assertEqual(expected_hashes_map, hashes_map['hash10'])
 
    def test_get_geo_hashes_map2(self):
        """ This test, given a latitude and longitude,
        expects to receive a map object with the value 'hash10' and key '7zzzzzzzzz'.

        Given:
            latitude=0.0, longitude=0.0

        Expects:
            {...'hash10': '7zzzzzzzzz', ...}
        """
        expected_hashes_map = '7zzzzzzzzz'
        hashes_map = firestore_database._get_geo_hashes_map(0.0, 0.0)
        self.assertEqual(expected_hashes_map, hashes_map['hash10'])
 
    def test_get_geo_hashes_map3(self):
        """ This test, given a latitude and longitude,
        expects to receive a map object with the value 'hash10' and key 'pbpbpbpbpb'.

        Given:
            latitude=-90, longitude=180

        Expects:
            {...'hash10': 'pbpbpbpbpb', ...}
        """
        expected_hashes_map = 'pbpbpbpbpb'
        hashes_map = firestore_database._get_geo_hashes_map(-90, 180)
        self.assertEqual(expected_hashes_map, hashes_map['hash10'])
    
    def test_get_date_fields(self):
        """ This test, given a datetime object,
        expects to receive a map object with the date fields parsed.
        """
        expected_date = {'year': 2019, 'month': 4, 'day': 13}
        date = firestore_database._get_date_fields(datetime.date(2019, 4, 13))
        self.assertEqual(expected_date, date)

    def test_get_max_visibility(
        self,
        first_visibility=data_types.VisibilityType.VISIBLE,
        second_visibility=data_types.VisibilityType.INVISIBLE,
        expected_visibility=data_types.VisibilityType.VISIBLE):
        """ This test, given two visibilities and an expected visibility,
        expects the max visibility to equal the expected visibility.

        """
        visibility = firestore_database._get_max_visibility(first_visibility, second_visibility)
        self.assertEqual(expected_visibility, visibility)


if __name__ == '__main__':
    unittest.main()
