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
from datetime import datetime
from backend_jobs.ingestion_pipeline.providers import image_provider_flickr


class TestFlickrProvider(unittest.TestCase):
    """ This class tests functions From the FlickerProvider class.
    """

    def test_get_date(self):
        """ This test, given an image with a date in the format of a string,
        expects to receive a new date in the format of datetime object.
        """
        image_with_datetaken = {
            'id': '39831840270', 'datetaken': '2018-04-22 16:41:11', 'ownername': 'Marian',
            'originalformat': 'jpg', 'latitude': '0', 'longitude': '0', 'height_o': '800', 'width_o': '533',
            'url': 'https://live.staticflickr.com/882/39831840270_ba571c8254_c.jpg'}
        expected_datetime_date_taken = datetime(2018, 4, 22, 16, 41, 11)
        date_taken = image_provider_flickr._get_date(image_with_datetaken)
        self.assertEqual(expected_datetime_date_taken, date_taken)

    def test_parse_query_arguments_given_tags_and_tagmode(self):
        """ This test, given a string of arguments,
        expects to receive a map object with the arguments parsed.

        Given:
            'tags:cat,plastic-tag_mode:any'

        Expects:
            {'tags': 'cat,plastic', 'tag_mode': 'any', 'text': ''}
        """
        query_arguments_string = 'tags:cat,plastic-tag_mode:any'
        expected_query_arguments_map = {'tags': 'cat,plastic', 'tag_mode': 'any', 'text': ''}
        query_arguments_map = image_provider_flickr._parse_query_arguments(query_arguments_string)
        self.assertEqual(expected_query_arguments_map, query_arguments_map)

    def test_parse_query_arguments_given_text(self):
        """ This test, given a string of arguments,
        expects to receive a map object with the arguments parsed.

        Given:
            'text:cat'

        Expects:
            {'tags': 'all', 'tag_mode': 'any', 'text': 'cat'}
        """
        query_arguments_string = 'text:cat'
        expected_query_arguments_map = {'tags': 'all', 'tag_mode': 'any', 'text': 'cat'}
        query_arguments_map = image_provider_flickr._parse_query_arguments(query_arguments_string)
        self.assertEqual(expected_query_arguments_map, query_arguments_map)

    def test_parse_query_arguments_given_tags(self):
        """ This test, given a string of arguments,
        expects to receive a map object with the arguments parsed.

        Given:
            'tags:cat,plastic'

        Expects:
            {'tags': 'cat,plastic', 'tag_mode': 'any', 'text': ''}
        """
        query_arguments_string = 'tags:cat,plastic'
        expected_query_arguments_map = {'tags': 'cat,plastic', 'tag_mode': 'any', 'text': ''}
        query_arguments_map = image_provider_flickr._parse_query_arguments(query_arguments_string)
        self.assertEqual(expected_query_arguments_map, query_arguments_map)


if __name__ == '__main__':
    unittest.main()
