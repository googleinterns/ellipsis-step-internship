import apache_beam as beam
import flickrapi
import requests
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from google.cloud import vision


# Use a service account
cred = credentials.Certificate('cred.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
client = vision.ImageAnnotatorClient()

class getUrl(beam.DoFn):
    def process(self, element):
        return [element[1].get('url_c')]

class getLabels(beam.DoFn):
    def process(self, element):
        image = vision.Image()
        image.source.image_uri = element
        response = client.label_detection(image=image)
        labels = response.label_annotations
        allLabels = [label.description for label in labels]
        return [(element, allLabels)]

class uploadToDatabase(beam.DoFn):
    def process(self, element):
        doc_ref = db.collection(u'images').document()
        doc_ref.set({
            u'url': element[0],
            u'labels': element[1],
        })
    
flickr = flickrapi.FlickrAPI('2d00397e012c30ccc33ca4fdc05a5c98', 'e36a277c77f09fdd', cache=True)
photos = flickr.walk(text='plasticbag',
                     tag_mode='all',
                     tags='plasticbag',
                     extras='url_c, geo, date_upload, date_taken, owner_name, icon_server',
                     per_page=100,  # may be you can try different numbers..
                     sort='relevance')

pipeline = beam.Pipeline()
images = (pipeline | "create" >> beam.Create(enumerate(photos))
| "url" >> beam.ParDo(getUrl()) 
| "label" >> beam.ParDo(getLabels())
| "upload" >> beam.ParDo(uploadToDatabase()))

# Run the pipeline
result = pipeline.run()

# lets wait until result a available
result.wait_until_finish()


