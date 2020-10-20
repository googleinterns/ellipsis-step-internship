from abc import ABC, abstractmethod
import apache_beam as beam
from google.cloud import vision_v1

class ImageRecognitionProvider(ABC, beam.DoFn):
    
    @abstractmethod
    def get_labels(self, element):
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
