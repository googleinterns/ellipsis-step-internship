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
from backend_jobs.ingestion_pipeline.pipeline_lib import data_types
from backend_jobs.ingestion_pipeline.providers.image_provider_flickr import FlickrProvider

IMAGE_PROVIDERS = {'FlickrProvider': FlickrProvider()}


class TestProviderIntrface(unittest.TestCase):
    """ This class is in charge of testing the image provider interface.
    """

    def test_get_images_and_exract_attributes(self):
        """ This test checks both the get_images function and the get_image_attributes function
        implementation for all providers.
        We test, given an image when calling the get_image_attributes function
        the output is in the right format.
        """
        for provider in IMAGE_PROVIDERS:
            current_provider = IMAGE_PROVIDERS[provider]
            images = current_provider.get_images(1)
            for image in images:
                image_attributes = current_provider.get_image_attributes(image)
                self.assertIsInstance(image_attributes, data_types.ImageAttributes)
                self.assertIsInstance(image_attributes.image_id, (str, type(None)))
                self.assertIsInstance(image_attributes.url, (str, type(None)))
                self.assertIsInstance(image_attributes.image_type, data_types.ImageType)
                self.assertIsInstance(image_attributes.date_shot, datetime)
                self.assertIsInstance(image_attributes.attribution, str)
                self.assertIsInstance(image_attributes.format, (str, type(None)))
                self.assertIsInstance(image_attributes.height_pixels, (int, type(None)))
                self.assertIsInstance(image_attributes.width_pixels, (int, type(None)))
                self.assertIsInstance(image_attributes.latitude, float)
                self.assertIsInstance(image_attributes.longitude, float)

    def test_get_num_of_batches(self):
        """ This test checks the get_num_of_batches function.
        We test wether the return value from the get_num_of_batches function
        is an int.
        """
        for provider in IMAGE_PROVIDERS:
            current_provider = IMAGE_PROVIDERS[provider]
            num_of_baches = current_provider.get_num_of_pages()
            self.assertIsInstance(num_of_baches, int)


if __name__ == '__main__':
    unittest.main()
