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

An Image Recognition pipeline to label images from specific dataset by a specific provider.

The pipeline uses Python's Apache beam library to parralize the different stages.
The images are taken from a Firestore database and are labeled by a ML provider.
The labeling content is updated in the database for each image.
By the end of the process, the project's admin group get notified.
"""

from __future__ import absolute_import

import argparse
import logging
import random
from datetime import datetime

from past.builtins import unicode

from firebase_admin import firestore

import apache_beam as beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from providers import google_vision_api
from pipeline_lib.image_filtering import is_eligible
from pipeline_lib.redefine_labels import RedefineLabels

RANGE_OF_BATCH = 10 # Defines the range of the each batch for querying the database.
collection_name = 'Images'

def initialize_DB(): 
    """Initializes project's Firestore databse for writing and reading purposes.

    """
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        'projectId': 'step-project-ellispis',
        })
    return firestore.client()

def get_provider(provider_name):
    """ Creates an object of type ImageRecognitionProvider by the specific provider input.

    """ 
    if provider_name == 'Google_Vision_API':
        return google_vision_api.GoogleVisionAPI()
    
class GetDataset(beam.DoFn):
    """Queries the project's database to get the image dataset to label.

    """
    def setup(self):
        self.db = initialize_DB()

    def process(self, element, ingestion_provider = None, ingestion_run = None):
        """Queries firestore database for images from the ingestion_provider within a random range (by batch).
        
        Args:
            element: the lower limit for querying the database by the random field.
            ingestion_provider: the input of the pipeline, determines the images dataset.
            ingestion_run: the input of the pipeline, determines the dataset.

        Returns:
            A list of dictionaries with all the information (fields and id) of each one of the Firestore query's image documents.
        """
        random_min = element
        random_max = element+RANGE_OF_BATCH-1 # the higher limit for querying the database by the random field.
        # TODO: have different queries for ingestion provider and ingestion run once relevant data has been uploaded to Firestore by ingestion pipeline.
        if ingestion_provider:
            query = self.db.collection(collection_name).where(u'attribution', u'==', ingestion_provider).where(u'random', u'>=', random_min).where(u'random', u'<=', random_max).stream()
        else:
            query = self.db.collection(collection_name).where(u'attribution', u'==', ingestion_run).where(u'random', u'>=', random_min).where(u'random', u'<=', random_max).stream()
        return [add_id_to_dict(doc) for doc in query]

def add_id_to_dict(doc):
    full_dict = doc.to_dict()
    full_dict['id'] = doc.id
    return full_dict

class UploadToDatabase(beam.DoFn):
    """Uploads parallelly the label information parallelly to the project's database.

    """
    def setup(self):
        self.db = initialize_DB()

    def process(self, element, run_id):
        """Updates the project's database to contain documents with the currect fields for each label in the Labels subcollection of each image.

        Args: 
            element: tuple of image document dict and a list of all label Ids.
        """
        # TODO: need to figure out how to add the pipeline run's id inside the pipeline
        doc_id = element[0]['id']
        subcollection_ref = self.db.collection(collection_name).document(doc_id).collection(u'Labels')
        for label in element[1]:
            doc = subcollection_ref.document()
            doc.set({
                u'providerId': 'google_vision_api',
                u'providerVersion': '2.0.0',
                u'labelName': label['name'],
                u'visibility': 0,
                u'parentImageId': doc_id,
                u'pipelineRunId': run_id,
                u'hashmap': element[0]['hashmap']
            })
            if 'id' in label:
                doc.set({
                    u'labelId': label['id']
                }, merge = True)

def upload_to_pipeline_runs_collection(provider_Id, run_Id):
    """ Uploads inforamtion about the pipeline run to the Firestore collection
    """
    # TODO: get start, end and quality of current pipeline run.
    db = initialize_DB()
    db.collection(u'RecognitionPipelineRuns').document().set({
        u'providerId': provider_Id,
        u'startDate': 00,
        u'endDate': 00,
        u'quality': 00,
        u'visibility': 0,
        u'pipelineRunId': run_Id
    })

def run(argv=None, save_main_session=True):
  """Main entry point, defines and runs the image recognition pipeline."""
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input-ingestion-run',
      dest='input_ingestion_run',
      help='Input of ingestion pipeline run for images dataset.')
  parser.add_argument(
      '--input-ingestion-provider',
      dest='input_ingestion_provider',
      help='Input of ingestion pipeline provider for images dataset.')
  parser.add_argument(
      '--input-recognition-provider',
      dest='input_recognition_provider',
      required=True,
      default='Google_Vision_API',
      help='Input fimage recognition provider for labeling.')
  parser.add_argument(
      '--output',
      dest='output',
      help='Output file to write results to.')
  known_args, pipeline_args = parser.parse_known_args(argv)
  job_name = 'recognition-pipeline-run-{date_time}'.format(date_time = datetime.now())
 
  pipeline_options = PipelineOptions(pipeline_args)

  with beam.Pipeline(options=pipeline_options) as p:
    ingestion_run = known_args.input_ingestion_run
    ingestion_provider = known_args.input_ingestion_provider
    provider = get_provider(known_args.input_recognition_provider)
    # Creating an object of type ImageRecognitionProvider for the specific image recognition provider input 
    random_numbers = p | 'create' >> beam.Create([(1+10*i) for i in range(10)])
    if ingestion_run: # If the input that was given for specifing the images dataset was an ingestion run.
        dataset = random_numbers | 'get images dataset' >> beam.ParDo(GetDataset(), ingestion_run=ingestion_run)
    else:  # If the input that was given for specifing the images dataset was an ingestion provider.
        dataset = random_numbers | 'get images dataset' >> beam.ParDo(GetDataset(), ingestion_provider=ingestion_provider)
    # filtered_dataset = dataset | 'filter images' >> beam.Filter(is_eligible, provider.provider_Id) # need to add this back after having a relevant dataset from Tal's pipeline
    images_batch = dataset | 'combine to batches' >> beam.GroupBy(lambda doc: doc['random'])
    labels_batch = images_batch | 'label by batch' >> beam.ParDo(provider) # labels the images by the process method of the provider
    labels = labels_batch | 'flatten lists' >> beam.FlatMap(lambda elements: elements)
    labels_Id = labels | 'redefine labels' >> beam.ParDo(RedefineLabels(), provider.provider_Id)
    labels_Id | 'upload' >> beam.ParDo(UploadToDatabase(), job_name)
    upload_to_pipeline_runs_collection(provider.provider_Id, job_name)
    # TODO: add notification to admin group for verifying labels.
        
    if known_args.output: # For testing.
        def format_result(image, labels):
            return '%s: %s' % (image['url'], labels)
        output = labels_Id | 'Format' >> beam.MapTuple(format_result)
        output | 'Write' >> WriteToText(known_args.output)

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()