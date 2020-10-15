from __future__ import absolute_import

import argparse
import logging
import re
from google.cloud import vision

from past.builtins import unicode

from firebase_admin import firestore


import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import flickrapi

photos = ['https://live.staticflickr.com/7210/6843831417_861d6996e8_c.jpg']

def initializeDB(): 
    # Use the application default credentials 
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        'projectId': 'step-project-ellispis',
        })
    return firestore.client()

def callFlicker(pageNumber):
    flickr = flickrapi.FlickrAPI('2d00397e012c30ccc33ca4fdc05a5c98', 'e36a277c77f09fdd', cache=True)
    photos = flickr.photos.search(text='plasticbag',
                     tag_mode='all',
                     tags='plasticbag',
                     extras='url_c, geo, date_upload, date_taken, owner_name, icon_server',
                     per_page=10,  # may be you can try different numbers..
                     page=pageNumber,
                     sort='relevance')
    return photos[0]

class getUrl(beam.DoFn):
    def process(self, element):
        return [element.get('url_c')]

class getLabels(beam.DoFn):
    def process(self, element):
        if element:
            client = vision.ImageAnnotatorClient()
            image = vision.Image()
            image.source.image_uri = element
            response = client.label_detection(image=image)
            labels = response.label_annotations
            allLabels = [label.description for label in labels]
            return [(element, allLabels)]

class uploadToDatabase(beam.DoFn):
    def process(self, element):
        db = initializeDB()
        doc_ref = db.collection(u'imagesDemo2').document()
        doc_ref.set({
            u'url': element[0],
            u'labels': element[1],
        })

def run(argv=None, save_main_session=True):
  """Main entry point; defines and runs the wordcount pipeline."""
  parser = argparse.ArgumentParser()
#   parser.add_argument(
#       '--input',
#       dest='input',
#       default='gs://dataflow-samples/shakespeare/kinglear.txt',
#       help='Input file to process.')
  parser.add_argument(
      '--output',
      dest='output',
      required=True,
      help='Output file to write results to.')
  known_args, pipeline_args = parser.parse_known_args(argv)

  # We use the save_main_session option because one or more DoFn's in this
  # workflow rely on global context (e.g., a module imported at module level).
  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

  # The pipeline will be run on exiting the with block.
  with beam.Pipeline(options=pipeline_options) as p:

    createbatch = (p | 'createBatch' >> beam.Create([1,2,3]) )
    images1 = createbatch | 'callAPI' >> beam.ParDo(lambda x: callFlicker(x))
    images = images1 | 'url' >> beam.ParDo(getUrl())
    # images = p | 'create' >> beam.Create(photos)
    labels = images | 'label' >> beam.ParDo(getLabels())
    labels | 'upload' >> beam.ParDo(uploadToDatabase())

    # Format the counts into a PCollection of strings.
    def format_result(word, count):
      return '%s: %s' % (word, count)

    output = labels | 'Format' >> beam.MapTuple(format_result)

    # Write the output using a "Write" transform that has side effects.
    # pylint: disable=expression-not-assigned
    output | 'Write' >> WriteToText(known_args.output)


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()