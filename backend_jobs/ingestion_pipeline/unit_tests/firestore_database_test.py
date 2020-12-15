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


class TestFirestoreDatabase(unittest.TestCase):
  
    def test_get_geo_hashes_map1(self):
        expected_hashes_map = '9q8yvy60hd'
        hashes_map = firestore_database._get_geo_hashes_map(37.783371, -122.439687)
        self.assertEqual(expected_hashes_map, hashes_map['hash10'])
 
    def test_get_geo_hashes_map2(self):
        expected_hashes_map = '7zzzzzzzzz'
        hashes_map = firestore_database._get_geo_hashes_map(0.0, 0.0)
        self.assertEqual(expected_hashes_map, hashes_map['hash10'])
 
    def test_get_geo_hashes_map3(self):
        expected_hashes_map = 'pbpbpbpbpb'
        hashes_map = firestore_database._get_geo_hashes_map(-90, 180)
        self.assertEqual(expected_hashes_map, hashes_map['hash10'])
    
    def test_get_date_fields(self):
        expected_date = {'year': 2019, 'month': 4, 'day': 13}
        date = firestore_database._get_date_fields(datetime.date(2019, 4, 13))
        self.assertEqual(expected_date, date)


if __name__ == '__main__':
    unittest.main()
