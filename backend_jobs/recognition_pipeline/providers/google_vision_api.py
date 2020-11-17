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

from google.cloud import vision_v1
from backend_jobs.recognition_pipeline.pipeline_lib.image_recognition_provider import ImageRecognitionProvider
from backend_jobs.recognition_pipeline.filters.filter_by_format import FilterByFormat
from backend_jobs.recognition_pipeline.filters.filter_by_resolution import FilterByResolution

# pylint: disable=abstract-method
class GoogleVisionAPI(ImageRecognitionProvider):
    """ An implementation of the abstract class ImageRecognitionProvider
    specified for Google Vision API.

    """

    def setup(self):
        self.client = vision_v1.ImageAnnotatorClient()

    # pylint: disable=arguments-differ
    def process(self, element):
        features = [ {"type_": vision_v1.Feature.Type.LABEL_DETECTION} ]
        requests = []
        results = []
        docs = []
        for doc in element:
            url = doc['url']
            image = vision_v1.Image()
            image.source.image_uri = url
            request = vision_v1.AnnotateImageRequest(image= image, features=features)
            requests.append(request)
            docs.append(doc)
        batch_request = vision_v1.BatchAnnotateImagesRequest(requests=requests)
        response = self.client.batch_annotate_images(request=batch_request)
        for i, image_response in enumerate(response.responses):
            all_labels = [label.description.lower() for label in image_response.label_annotations]
            results.append([(docs[i], all_labels)])
        return results
 
    label_images = process
    prerequisites_map = {'format': FilterByFormat(\
        ['JPG', 'JPEG', 'PNG8', 'PNG24', 'GIF', 'BMP', 'WEBP', 'RAW', 'ICO', 'PDF', 'TIFF']),\
            'resolution': FilterByResolution({'height':480, 'width': 640})}
    provider_id='Google_Vision_API'
    provider_version='2.0.0'
