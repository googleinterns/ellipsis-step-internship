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

from abc import ABC, abstractmethod
import apache_beam as beam
from google.cloud import vision_v1

class ImageRecognitionProvider(ABC, beam.DoFn):
    """ Each recognition provider used in our project will have an implementation of this abstract class.
    
    All recognition providers need to have a method for labeling the images, 
    an Id property and the latest version.
    """
    
    @abstractmethod
    def get_labels(self, element):
        """Labels a batch of images from dataset using a specific recognition provider.

        Args:
            element: a tuple of a random number and a list of images information dictionaries.

        Returns:
            list of lists in which each inner list is a tuple of a image dictionary and all labels recognixed in it by the provider.
        """
        pass

    @property
    def provider_Id(self):
        raise NotImplementedError

    @property
    def provider_Version(self):
        raise NotImplementedError

class GoogleVisionAPI(ImageRecognitionProvider):
    def get_labels(self, element):
        client = vision_v1.ImageAnnotatorClient()
        features = [ {"type_": vision_v1.Feature.Type.LABEL_DETECTION} ]
        requests = []
        results = []
        docs = []
        for doc in element[1]:
            url = doc['url']
            if url:
                image = vision_v1.Image()
                image.source.image_uri = url
                request = vision_v1.AnnotateImageRequest(image= image, features=features)
                requests.append(request)
                docs.append(doc)
        batchRequest = vision_v1.BatchAnnotateImagesRequest(requests=requests)
        response = client.batch_annotate_images(request=batchRequest)
        for i, image_response in enumerate(response.responses):
            allLabels = [label.description for label in image_response.label_annotations]
            results.append([(docs[i], allLabels)])
        return results
    provider_Id='Google_Vision_API'
    provider_Version='2.0.0'
