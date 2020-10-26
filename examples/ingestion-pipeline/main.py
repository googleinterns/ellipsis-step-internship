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

from __future__ import absolute_import
import argparse
import logging
from past.builtins import unicode
import apache_beam as beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
import flickrapi
from providers import imageProviderFlickr

def initialize_database(): 
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        'projectId': 'step-project-ellispis',
        })
    return firestore.client()

class UploadToDatabase(beam.DoFn):
    def setup(self):
        self.db = initialize_database()
    def process(self, element):
        #TODO: convert location to firestore.GeoPoint
        doc_ref = self.db.collection(u'imagesDemoTal2').document()
        doc_ref.set({
            u'url': element.url,
            u'coordinates': element.location,
            u'date_upload': element.date_upload,
            u'date_taken': element.date_taken,
            u'imageAttributes': 
            {'format': element.format, u'resolution':element.resolution},
            u'attribution': element.attribution,
            u'random': random.randint(1,101)
            #TODO: add subcollection pipeline run
        })

#TODO: write a filtering function that takes into consideration all attributes
#such as invalid resolution date and more
def filtered_images(element):
    return element.url != None and element.location[0] != '0'

#TODO: Find a way to make this more dynamic
def get_image_provider(provider_name):
    if 'FlickerProvider' == provider_name:
        return imageProviderFlickr.FlickerProvider()

def run(argv=None, save_main_session=True):
  """Main entry point; defines and runs the image ingestion pipeline."""
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input',
      default='FlickerProvider',
      help='Provider name to process.')
  parser.add_argument(
      '--output',
      dest='output',
      help='Output file to write results to.')
  known_args, pipeline_args = parser.parse_known_args(argv)
  pipeline_options = PipelineOptions(pipeline_args)

  # The pipeline will be run on exiting the with block.
  with beam.Pipeline(options=pipeline_options) as p:
    ApiProvider= get_image_provider(known_args.input)
    num= ApiProvider.get_num_of_batches()
    create_batch = (p | 'create' >> beam.Create([i for i in range(1, int(3)+1, 1)]) )
    images = create_batch | 'call API' >> beam.ParDo(ApiProvider.get_images)
    extracted_element = images | 'extract attributes' >> beam.Map(ApiProvider.get_image_attributes)
    filtered_element = extracted_element | 'filter' >> beam.Filter(filtered_images) 
    filtered_element | 'upload' >> beam.ParDo(UploadToDatabase())

    if known_args.output:
        filtered_element | 'Write' >> WriteToText(known_args.output)

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
  