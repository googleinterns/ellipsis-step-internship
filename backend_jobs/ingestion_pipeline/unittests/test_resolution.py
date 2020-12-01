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
from backend_jobs.ingestion_pipeline.providers import image_provider_flickr


class TestFlickrProvider(unittest.TestCase):

    first_image = {
        'id': '39831840270', 'datetaken': '2018-04-22 16:41:11', 'ownername': 'Marian',
        'originalformat': 'jpg', 'latitude': '0', 'longitude': '0', 'height_c': '800', 'width_c': '533',
        'url': 'https://live.staticflickr.com/882/39831840270_ba571c8254_c.jpg'}

    second_image = {
        'id': '39831840270', 'datetaken': '2018-04-22 16:41:11', 'ownername': 'Marian',
        'originalformat': 'jpg', 'latitude': '0', 'longitude': '0', 'height_c': '800', 'width_c': '533',
        'url': 'https://live.staticflickr.com/882/39831840270_ba571c8254.jpg'}     

    def test_get_url_by_resolution1(self):
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(500, 200, self.first_image)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254_m.jpg'
        self.assertEqual(expected_url, new_url)
    
    def test_get_url_by_resolution2(self):
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(300, 500, self.first_image)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254_n.jpg'
        self.assertEqual(expected_url, new_url)

    def test_get_url_by_resolution3(self):
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(600, 600, self.first_image)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254_z.jpg'
        self.assertEqual(expected_url, new_url)

    def test_get_url_by_resolution4(self):
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(500, 450, self.first_image)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254.jpg'
        self.assertEqual(expected_url, new_url)

    def test_get_url_by_resolution5(self):
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(500, 200, self.second_image)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254_m.jpg'
        self.assertEqual(expected_url, new_url)
    
    def test_get_url_by_resolution6(self):
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(300, 500, self.second_image)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254_n.jpg'
        self.assertEqual(expected_url, new_url)

    def test_get_url_by_resolution7(self):
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(600, 600, self.second_image)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254_z.jpg'
        self.assertEqual(expected_url, new_url)

    def test_get_url_by_resolution8(self):
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(500, 450, self.second_image)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254.jpg'
        self.assertEqual(expected_url, new_url)


if __name__ == '__main__':
    unittest.main()
