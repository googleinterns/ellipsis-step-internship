from pipeline_lib.image_recognition_provider import ImageRecognitionProvider
from google.cloud import vision_v1

class GoogleVisionAPI(ImageRecognitionProvider):

    def setup(self):
        self.client = vision_v1.ImageAnnotatorClient()

    def process(self, element):
        features = [ {"type_": vision_v1.Feature.Type.LABEL_DETECTION} ]
        requests = []
        results = []
        docs = []
        for doc in element[1]:
            url = doc['url']
            image = vision_v1.Image()
            image.source.image_uri = url
            request = vision_v1.AnnotateImageRequest(image= image, features=features)
            requests.append(request)
            docs.append(doc)
        batchRequest = vision_v1.BatchAnnotateImagesRequest(requests=requests)
        response = self.client.batch_annotate_images(request=batchRequest)
        for i, image_response in enumerate(response.responses):
            allLabels = [label.description for label in image_response.label_annotations]
            results.append([(docs[i], allLabels)])
        return results
    
    get_labels = process
    provider_Id='Google_Vision_API'
    provider_Version='2.0.0'
