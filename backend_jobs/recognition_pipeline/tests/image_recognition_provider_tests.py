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
from backend_jobs.recognition_pipeline.providers.google_vision_api import GoogleVisionAPI

_SIZE_OF_LARGE_BATCH = 1000

class TestImageRecognitionProviders(unittest.TestCase):
    """ Tests ImageRecognitionProvider interface implementations.

    """
    def setUp(self):
        self.eligible_image1= {'url': \
            'https://live.staticflickr.com/3677/13545844805_170ec3746b_c.jpg',\
                'imageAttributes':{'format': 'jpg', 'resolution': {'width': 800, 'height': 600}},\
                    'ingestedProviders': []}
        self.eligible_image2 =  {'url':\
            'https://live.staticflickr.com/5284/5338762379_59f7435b93_c.jpg',\
                'imageAttributes': {'format': 'pdf', 'resolution': {'width': 800, 'height': 600}},\
                    'ingestedProviders': []}
        self.uneligible_image = {'url':\
            'https://live.staticflickr.com/5284/5338762379_59f7435b93_c.jpg',\
                'imageAttributes': {'format': 'pdf', 'resolution': {'width': 200, 'height': 200}},\
                    'ingestedProviders': []}
        self.image_batch = [self.eligible_image1, self.eligible_image2]
        self.providers = [GoogleVisionAPI()]

    def test_label_images_correctly(self):
        """ Tests the get_labels method of each one of the providers.

        """
        for provider in self.providers:
            provider.setup()
            images_and_labels = provider.process(self.image_batch)
            image1_and_labels = images_and_labels[0][0]
            image1 = image1_and_labels[0]
            image1_labels = image1_and_labels[1]
            image2_and_labels = images_and_labels[1][0]
            image2 = image2_and_labels[0]
            image2_labels = image2_and_labels[1]
            # Checks that the image returned is the same as the image sent.
            self.assertEqual(image1, self.eligible_image1)
            # Checks that the 'label images' method did recognize the cat in the image.
            self.assertTrue('cat' in image1_labels)
            # Checks that the image returned is the same as the image sent.
            self.assertEqual(image2, self.eligible_image2)
            # Checks that the 'label images' method did recognize the dog in the image.
            self.assertTrue('dog' in image2_labels)

    def test_label_large_batch_of_images(self):
        """ Tests labeling a large batch of images at once.

        """
        image_batch = [self.eligible_image1 for i in range(_SIZE_OF_LARGE_BATCH)]
        for provider in self.providers:
            provider.setup()
            images_and_labels = provider.process(image_batch)
            # Checks if no images were lost on the way.
            self.assertEqual(len(images_and_labels), _SIZE_OF_LARGE_BATCH)
            prev_image = images_and_labels[0][0][0]
            prev_labels = images_and_labels[0][0][1]
            self.assertGreater(len(prev_labels), 0) # Checks that at least one label was recognized.
            for i in range(_SIZE_OF_LARGE_BATCH-1):
                next_image = images_and_labels[i+1][0][0]
                next_labels = images_and_labels[i+1][0][1]
                # Checks that all images are still the same.
                self.assertEqual(prev_image, next_image)
                # Checks that all labels returned are the same.
                self.assertEqual(prev_labels, next_labels)
                prev_image = next_image
                prev_labels = next_labels

    def test_is_eligible(self):
        """ Tests both supported and unsupported images by is_eligible method
            of each provider.
            
        """
        for provider in self.providers:
            self.assertTrue(provider.is_eligible(self.eligible_image1))
            self.assertFalse(provider.is_eligible(self.uneligible_image))

if __name__ == '__main__':
    unittest.main()
