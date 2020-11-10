import unittest
from providers.google_vision_api import GoogleVisionAPI

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
        self.image_batch = [0, [self.eligible_image1, self.eligible_image2]]
        self.providers = [GoogleVisionAPI()]

    def test_get_labels(self):
        """ Tests the get_labels method of each one of the providers.

        """
        for provider in self.providers:
            batch_labels = provider.get_labels(self.image_batch)
            image1_and_labels = batch_labels[0][0]
            image2_and_labels = batch_labels[1][0]
            self.assertEqual(image1_and_labels[0], self.eligible_image1)
            self.assertTrue('cat' in image1_and_labels[1])
            self.assertEqual(image2_and_labels[0], self.eligible_image2)
            self.assertTrue('dog' in image2_and_labels[1])

    def test_is_eligible(self):
        """ Tests both supported and unsupported images by is_eligible method
            of each provider.

        """
        for provider in self.providers:
            self.assertTrue(provider.is_eligible(self.eligible_image1))
            self.assertFalse(provider.is_eligible(self.uneligible_image))

if __name__ == '__main__':
    unittest.main()
