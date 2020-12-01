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
    element =  {'id': '39831840270', 'datetaken': '2018-04-22 16:41:11',
        'ownername': 'Marian Kloon (on and off)', 'originalformat': 'jpg',
        'latitude': '0', 'longitude': '0','height_c': '800', 'width_c': '533',
        'url': 'https://live.staticflickr.com/882/39831840270_ba571c8254_c.jpg'}
        
    def get_date(self):
        string_datetime = '2009-10-11 18:21:15'
        converted_datetime = datetime.strptime(string_datetime, '%Y-%m-%d %H:%M:%S')
        expected_datetime = image_provider_flickr.get_date(self.element)
        self.assertEqual(expected_datetime, converted_datetime)
    
    def test_get_coordinates1(self):
        self.element['latitude']='0.0'
        self.element['longitude']='0.0'
        expected_coordinates = image_provider_flickr.get_coordinates(self.element)
        self.assertEqual(expected_coordinates, None)
    
    def test_get_coordinates2(self):
        coordinates = {'latitude':60.98,'longitude':60.98}
        self.element['latitude']='60.98'
        self.element['longitude']='60.98'
        expected_coordinates = image_provider_flickr.get_coordinates(self.element)
        self.assertEqual(expected_coordinates, coordinates)
    
    def test_get_resolution(self):
        resolution = {'height':800,'width':533}
        expected_resolution = image_provider_flickr.get_resolution(self.element)
        self.assertEqual(expected_resolution, resolution)
    
    def test_get_url_by_resolution1(self):
        flicker_provider=image_provider_flickr.FlickrProvider()
        new_url= flicker_provider.get_url_for_max_resolution(
            {'height':500,'width':200},
            self.element)
        expected_url='https://live.staticflickr.com/882/39831840270_ba571c8254.jpg'
        self.assertEqual(expected_url, new_url)
    
    def test_get_url_by_resolution2(self):
        flicker_provider=image_provider_flickr.FlickrProvider()
        new_url= flicker_provider.get_url_for_max_resolution(
            {'height':300,'width':200},
            self.element)
        expected_url='https://live.staticflickr.com/882/39831840270_ba571c8254_n.jpg'
        self.assertEqual(expected_url, new_url)
 
 
if __name__ == '__main__':
   unittest.main()
