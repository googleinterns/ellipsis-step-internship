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
from backend_jobs.recognition_pipeline.pipeline_lib.image_recognition_provider\
    import ImageRecognitionProvider
from backend_jobs.pipeline_utils import database_schema

# pylint: disable=abstract-method
class GoogleVisionAPI(ImageRecognitionProvider):
    """ An implementation of the abstract class ImageRecognitionProvider
    specified for Google Vision API.

    """

    def setup(self):
        self.client = vision_v1.ImageAnnotatorClient()

    # pylint: disable=arguments-differ
    def process(self, element):
        images_and_labels = []
        for i in range(0, len(element), 2000): # The provider supports a batch of max 2000 images.
            images_and_labels.extend(self._get_labels_of_batch(element[i:2000+i]))
        return images_and_labels

    def _get_labels_of_batch(self, image_docs):
        """ Labels the images in the batch using one call to the Google Vision API.
            Used to label each batch in the class's process method.

        Args:
            image_docs: list of up to 2000 image docs represented by dictionaries.

        """
        features = [ {"type_": vision_v1.Feature.Type.LABEL_DETECTION} ]
        requests = []
        results = []
        docs = []
        i = 0
        for doc in image_docs:
            url = doc[database_schema.COLLECTION_IMAGES_FIELD_URL]
            image = vision_v1.Image()
            image.source.image_uri = url
            request = vision_v1.AnnotateImageRequest(image=image, features=features)
            requests.append(request)
            docs.append(doc)
        batch_request = vision_v1.BatchAnnotateImagesRequest(requests=requests)
        response = self.client.batch_annotate_images(request=batch_request)
        for i, image_response in enumerate(response.responses):
            all_labels = [label.description.lower() for label in image_response.label_annotations]
            results.append([(docs[i], all_labels)])
        return results

    _resolution_prerequisites = {'height':480, 'width': 640}
    _format_prerequisites =  ['JPG', 'JPEG', 'PNG8', 'PNG24', 'GIF', \
        'BMP', 'WEBP', 'RAW', 'ICO', 'PDF', 'TIFF']
    provider_id='Google_Vision_API'
    provider_version='2.0.0'
