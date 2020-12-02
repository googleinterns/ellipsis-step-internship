
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


class TestFlickrProviderResolutionFunction(unittest.TestCase):
    """ This class tests get_url_for_min_resolution flicker implantation function.
    This function gets a resolution(min height and min width) and an image and generates a new url
    with the closest above fit required resolution.
    In flickr the resolution is represented in the url.
    See details at https://www.flickr.com/services/api/misc.urls.html
    """

    image_with_url_resolution = {
        'id': '39831840270', 'datetaken': '2018-04-22 16:41:11', 'ownername': 'Marian',
        'originalformat': 'jpg', 'latitude': '0', 'longitude': '0', 'height_o': '800', 'width_o': '533',
        'url': 'https://live.staticflickr.com/882/39831840270_ba571c8254_c.jpg'}

    image_without_url_resolution = {
        'id': '39831840270', 'datetaken': '2018-04-22 16:41:11', 'ownername': 'Marian',
        'originalformat': 'jpg', 'latitude': '0', 'longitude': '0', 'height_o': '800', 'width_o': '533',
        'url': 'https://live.staticflickr.com/882/39831840270_ba571c8254.jpg'}

    flicker_provider = image_provider_flickr.FlickrProvider()

    def test_get_url_for_min_resolution_return_320_resolution(self):
        """ Given a url with a max resolution of 800, min height of 300 and min width of 200,
        expects to receive a new url with closest above fit resolution of 300.

        Expects:
            Url with max resolution of 320. (n represents max resolution of 320)
        """
        new_url = self.flicker_provider.get_url_for_min_resolution(300, 200, self.image_with_url_resolution)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254_n.jpg'
        self.assertEqual(expected_url, new_url)

    def test_get_url_for_min_resolution_return_1024_resolution(self):
        """ Given a url with a max resolution of 800, min height of 850 and min width of 1000,
        expects to receive a new url with closest above fit resolution of 1000.

        Expects:
            Url with max resolution of 1024. (b represents max resolution of 1024)
        """
        new_url = self.flicker_provider.get_url_for_min_resolution(850, 1000, self.image_with_url_resolution)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254_b.jpg'
        self.assertEqual(expected_url, new_url)

    def test_get_url_for_min_resolution_return_240_resolution(self):
        """ Given a url with a max resolution of 500, min height of 100 and min width of 210,
        expects to receive a new url with closest above fit resolution of 210.

        Expects:
            Url with max resolution of 240. (m represents max resolution of 240)
        """
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(100, 210, self.image_without_url_resolution)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254_m.jpg'
        self.assertEqual(expected_url, new_url)

    def test_get_url_for_min_resolution_return_800_resolution(self):
        """ Given a url with a max resolution of 500, min height of 600 and min width of 750,
        expects to receive a new url with closest above fit resolution of 750.

        Expects:
            Url with max resolution of 800. (c represents max resolution of 800)
        """
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(600, 750, self.image_without_url_resolution)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254_c.jpg'
        self.assertEqual(expected_url, new_url)

    def test_get_url_for_min_resolution_return_500_resolution_first(self):
        """ Given a url with a max resolution of 800, min height of 480 and min width of 450,
        expects to receive a new url with closest above fit resolution of 480.

        Expects:
            Url with max resolution of 500. (no char represents max resolution of 500)
        """       
        new_url = self.flicker_provider.get_url_for_min_resolution(480, 450, self.image_with_url_resolution)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254.jpg'
        self.assertEqual(expected_url, new_url)

    def test_get_url_for_min_resolution_return_500_resolution_second(self):
        """ Given a url with a max resolution of 500, min height of 500 and min width of 500,
        expects to receive a new url with closest above fit resolution of 500.

        Expects:
            Url with max resolution of 500. (no char represents max resolution of 500)
        """
        flicker_provider = image_provider_flickr.FlickrProvider()
        new_url = flicker_provider.get_url_for_min_resolution(500, 500, self.image_without_url_resolution)
        expected_url = 'https://live.staticflickr.com/882/39831840270_ba571c8254.jpg'
        self.assertEqual(expected_url, new_url)


if __name__ == '__main__':
    unittest.main()
