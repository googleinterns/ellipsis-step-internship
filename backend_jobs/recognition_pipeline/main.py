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

The pipeline uses Python's Apache beam library to parallelize the different stages.
The images are taken from a Firestore database and are labeled by a ML provider.
The labeling content is updated in the database for each image.
By the end of the process, the project's admin group get notified.
"""

from __future__ import absolute_import

import argparse
import logging
from datetime import datetime

import apache_beam as beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions

from providers import google_vision_api
from pipeline_lib.redefine_labels import RedefineLabels
from pipeline_lib.notify_admins import send_email_to_notify_admins
from pipeline_lib.firestore_database import\
    GetBatchedDataset, UploadToDatabase, upload_to_pipeline_runs_collection

NAME_TO_PROVIDER = {'Google_Vision_API': google_vision_api.GoogleVisionAPI()}
# Maps recognition provider names to an object of the provider.

def get_provider(provider_name):
    """ Creates an object of type ImageRecognitionProvider by the specific provider input.

    """
    if provider_name in NAME_TO_PROVIDER:
        return NAME_TO_PROVIDER[provider_name]
    raise ValueError('{provider} is an unknown image recognition provider'\
        .format(provider = provider_name))

def run(argv=None):
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
        help='Input image recognition provider for labeling.')
    parser.add_argument(
        '--output',
        dest='output',
        help='Output file to write results to for testing.')
    known_args, pipeline_args = parser.parse_known_args(argv)
    job_name = 'recognition-pipeline-run-{date_time}'.format(date_time = datetime.now())

    pipeline_options = PipelineOptions(pipeline_args)

    with beam.Pipeline(options=pipeline_options) as p:
        ingestion_run = known_args.input_ingestion_run
        ingestion_provider = known_args.input_ingestion_provider
        recognition_provider = get_provider(known_args.input_recognition_provider)
        # Creating an object of type ImageRecognitionProvider
        # for the specific image recognition provider input
        random_numbers = p | 'create' >> beam.Create([(1+10*i) for i in range(10)])
        if ingestion_run:
            # If the input was for specifing the images dataset was an ingestion run.
            dataset = random_numbers | 'get images dataset' >> \
                beam.ParDo(GetBatchedDataset(), ingestion_run=ingestion_run)
        else:
            # If the input was for specifing the images dataset was an ingestion provider.
            dataset = random_numbers | 'get images dataset' >> \
                beam.ParDo(GetBatchedDataset(), ingestion_provider=ingestion_provider)
        filtered_dataset = dataset | 'filter images' >> \
            beam.Filter(recognition_provider.is_eligible)
        images_batch = filtered_dataset | 'combine to batches' >> \
            beam.GroupBy(lambda doc: doc['random'])
        labelled_images_batch = images_batch | 'label by batch' >> \
            beam.ParDo(recognition_provider)
            # labels the images by the process method of the provider.
        labelled_images = labelled_images_batch | \
            beam.FlatMap(lambda elements: elements)
        labels_id = labelled_images | 'redefine labels' >> \
            beam.ParDo(RedefineLabels(), recognition_provider.provider_id)
        # pylint: disable=expression-not-assigned
        labels_id | 'upload' >> beam.ParDo(UploadToDatabase(), job_name)
        upload_to_pipeline_runs_collection(recognition_provider.provider_id, job_name)
        if ingestion_run:
            send_email_to_notify_admins(job_name=job_name, ingestion_run=ingestion_run)
        else:
            send_email_to_notify_admins(job_name=job_name, ingestion_provider=ingestion_provider)

        if known_args.output: # For testing.
            def format_result(image, labels):
                return '%s: %s' % (image['url'], labels)
            output = labels_id | 'Format' >> beam.MapTuple(format_result)
            output | 'Write' >> WriteToText(known_args.output)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
