"""An Image Recognition pipeline to label images from specific dataset by a specific provider.

The pipeline uses Python's Apache beam library to parralize the different stages.
The images are taken from a Firestore database and are labeled by a ML provider.
The labeling content is updated in the database for each image.
By the end of the process, the project's admin group get notified.
"""

from __future__ import absolute_import

import argparse
import logging
import re
import random

from google.cloud import vision
from google.cloud import vision_v1

from past.builtins import unicode

from firebase_admin import firestore

import apache_beam as beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from additional_files_dir.interface import GoogleVisionAPI

# TODO: Think about whether to do this in the same map, or change to ids inside the redefine method
LABEL_TO_ID = {'bag': 'GaveDiWni9CzOp6eYRDE'}
REDEFINE_LABELS = {'Google_Vision_API':{'Bag': LABEL_TO_ID['bag'], 'Glass': LABEL_TO_ID['bag']}} #TODO: fill this map
PREREQUISITES_MAP = {'Google_Vision_API': {'format':['JPEG', 'PNG8', 'PNG24', 'GIF', 'BMP', 'WEBP', 'RAW', 'ICO', 'PDF', 'TIFF'], 'minimun_size':'300'}}

def initialize_DB(): 
    '''Initializes project's Firestore databse for writing and reading purposes.'''
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        'projectId': 'step-project-ellispis',
        })
    return firestore.client()

def get_provider(provider_name):
    if provider_name == 'Google_Vision_API':
        return GoogleVisionAPI()

def get_dataset(random_min, random_max, ingestion_provider):
    '''Queries firestore database for images from the ingestion_provider within a random range (by batch).
    
    Args:
        random_min: the lower limit for querying the database by the random field
        random_max: the higher limit for querying the database by the random field
        ingestion_provider: the input of the pipeline, determines the images dataset.

    Returns:
        A list of dictionaries with all the information (fields and id) of each one of the Firestore query's image documents
    '''
    # TODO: have different queries for ingestion provider and ingestion run
    db = initialize_DB()
    query = db.collection(u'Images').where(u'attribution', u'==', ingestion_provider).where(u'random', u'>=', random_min).where(u'random', u'<=', random_max).stream()
    return [add_id_to_dict(doc) for doc in query]

def add_id_to_dict(doc):
    full_dict = doc.to_dict()
    full_dict['id'] = doc.id
    return full_dict

def is_eligible(image, provider):
    for criteria in PREREQUISITES_MAP[provider]:
        if not is_supported(image, criteria):
            return False
    return True

def is_supported(image, criteria):
    # TODO: not implemnted yet. Should it be switch-case for each different condition?
    return True

class RedefineLabels(beam.DoFn):
    '''Converts parallelly the labels list returned from the provider to the corresponding label Id's.

    '''
    def process(self, element, provider):
        '''Uses the global redefine map to change the different labels to the project's label Ids.

        Args:
            element: (dictionary of image properties, labels list)
            provider: image recognition provider for the redefine map

        Returns:
            [(dictionary of image properties, label ids list)] 
        '''
        all_label_Ids = []
        for label in element[1]:
            if label in REDEFINE_LABELS[provider]: 
                labelId = REDEFINE_LABELS[provider][label]
                all_label_Ids.append(labelId)
        if all_label_Ids:
            return [(element[0], all_label_Ids)]

class UploadToDatabase(beam.DoFn):
    '''Uploads parallelly the label informtion parallelly tp the project's database.

    '''
    def process(self, element):
        '''Updates the project's database to contain documents with the currect fields for each label in the Labels subcollection of each image.

        Args: 
            element: (element[0], all_label_Ids)
        '''
        # TODO: need to figure out how to add the pipeline run's id inside the pipeline
        db = initialize_DB()
        doc_id = element[0]['id']
        subcollection_ref = db.collection(u'Images').document(doc_id).collection(u'Labels')
        for label in element[1]:
            subcollection_ref.document().set({
                u'providerId': 'google_vision_api',
                u'providerVersion': '2.0.0',
                u'labelId': label,
                u'visibility': 0,
                u'parentImageId': doc_id
            })

def run(argv=None, save_main_session=True):
  """Main entry point, defines and runs the image recognition pipeline."""
  parser = argparse.ArgumentParser()
  # TODO: need to support input of either an ingestion run or an ingestion provider
#   parser.add_argument(
#       '--input-dataset-run',
#       dest='input0',
#       help='Input of ingestion pipeline run for images dataset.')
  parser.add_argument(
      '--input-dataset-provider',
      dest='input1',
      help='Input of ingestion pipeline provider for images dataset.')
  parser.add_argument(
      '--input-provider',
      dest='input2',
      required=True,
      help='Input fimage recognition provider for labeling.')
  parser.add_argument(
      '--output',
      dest='output',
      required=True,
      help='Output file to write results to.')
  known_args, pipeline_args = parser.parse_known_args(argv)

  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

  with beam.Pipeline(options=pipeline_options) as p:
    attributer = known_args.input1
    provider = get_provider(known_args.input2)
    random_numbers = p | 'create' >> beam.Create([(1+10*i) for i in range(10)])
    dataset = random_numbers | 'get images dataset' >> beam.ParDo(lambda x: get_dataset(x, x+9, attributer))
    filtered_dataset = dataset | 'filter images' >> beam.Filter(is_eligible, provider.provider_Id)
    images_batch = filtered_dataset | 'combine to batches' >> beam.GroupBy(lambda doc: doc['random'])
    label_batch = images_batch | 'label by batch' >> beam.ParDo(provider.get_labels) 
    labels = labels_batch | 'flatten lists' >> beam.FlatMap(lambda elements: elements)
    labels_Id = labels | 'redefine labels' >> beam.ParDo(RedefineLabels(), provider.provider_Id)
    labels_Id | 'upload' >> beam.ParDo(UploadToDatabase())
    

    
    def format_result(image, labels):
      return '%s: %s' % (image['url'], labels)

    output = labels_Id | 'Format' >> beam.MapTuple(format_result)

    # Write the output using a "Write" transform that has side effects.
    output | 'Write' >> WriteToText(known_args.output)


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()