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
import random

from google.cloud import vision
from google.cloud import vision_v1

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

def initialize_DB(): 
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        'projectId': 'step-project-ellispis',
        })
    return firestore.client()

class Flicker(beam.DoFn):
    def call_flicker(self,pageNumber):
        flickr = flickrapi.FlickrAPI('2d00397e012c30ccc33ca4fdc05a5c98', 'e36a277c77f09fdd', cache=True)
        photos = flickr.photos.search(text='plasticbag',
                        tag_mode='all',
                        tags='plasticbag',
                        extras='url_c, geo, date_upload, date_taken, owner_name, icon_server',
                        per_page=10,  # may be you can try different numbers..
                        page=pageNumber,
                        sort='relevance')
        return photos[0]
    def get_num_of_batches(self):
        API=Flicker()
        photos=API.call_flicker(1)
        return (photos.attrib['pages'])
    def get_url(self, element):
        return [(get_random_key(), element.get('url_c'))]


def get_random_key():
        return random.randint(1, 10)

class GetLabelsByBatch(beam.DoFn):
    def process(self, element):
        client = vision_v1.ImageAnnotatorClient()
        features = [ {"type_": vision_v1.Feature.Type.LABEL_DETECTION} ]
        requests = []
        results = []
        urls = []
        for url in element[1]:
            if url:
                image = vision_v1.Image()
                image.source.image_uri = url
                request = vision_v1.AnnotateImageRequest(image= image, features=features)
                requests.append(request)
                urls.append(url)
        batchRequest = vision_v1.BatchAnnotateImagesRequest(requests=requests)
        response = client.batch_annotate_images(request=batchRequest)
        for i, image_response in enumerate(response.responses):
            allLabels = [label.description for label in image_response.label_annotations]
            results.append([(urls[i], allLabels)])
        return results

class UploadToDatabase(beam.DoFn):
    def setup(self):
        self.db = initialize_DB()
    def process(self, element):
        doc_ref = self.db.collection(u'imagesDemo10').document()
        doc_ref.set({
            u'url': element[0],
            u'labels': element[1],
        })

def run(argv=None, save_main_session=True):
  """Main entry point; defines and runs the ingestion and labeling pipeline."""
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--output',
      dest='output',
      help='Output file to write results to.')
  known_args, pipeline_args = parser.parse_known_args(argv)

  # We use the save_main_session option because one or more DoFn's in this
  # workflow rely on global context (e.g., a module imported at module level).
  pipeline_options = PipelineOptions(pipeline_args)

  # The pipeline will be run on exiting the with block.
  with beam.Pipeline(options=pipeline_options) as p:

    API=Flicker()
    createbatch = (p | 'create' >> beam.Create([1,2,3]) )
    images = createbatch | 'call Flicker API' >> beam.ParDo(API.call_flicker)
    urls = images | 'get url' >> beam.ParDo(lambda  elament: API.get_url(elament))
    imagesBatch = urls | 'combine' >> beam.GroupByKey()
    labelsBatch = imagesBatch | 'label by batch' >> beam.ParDo(GetLabelsByBatch()) 
    labels = labelsBatch | 'Flatten lists' >> beam.FlatMap(lambda elements: elements)
    labels | 'upload' >> beam.ParDo(UploadToDatabase())

    # Format the counts into a PCollection of strings.
    def format_result(word, count):
      return '%s: %s' % (word, count)

    if known_args.output:
        output = labels | 'Format' >> beam.MapTuple(format_result)

        # Write the output using a "Write" transform that has side effects.
        # pylint: disable=expression-not-assigned
        output | 'Write' >> WriteToText(known_args.output)


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()