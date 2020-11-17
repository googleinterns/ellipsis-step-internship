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
# from apache_beam.runners.dataflow.internal.apiclient import DataflowApplicationClient
from providers import google_vision_api
from backend_jobs.recognition_pipeline.pipeline_lib.redefine_labels import RedefineLabels
from pipeline_lib.notify_admins import send_email_to_notify_admins
from backend_jobs.recognition_pipeline.pipeline_lib.firestore_database import\
    GetBatchedImageDataset, StoreInDatabase, get_redefine_map
from backend_jobs.pipeline_utils.firestore_database import upload_to_pipeline_runs_collection
from backend_jobs.pipeline_utils.utils import get_provider, get_timestamp_id

NAME_TO_PROVIDER = {'Google_Vision_API': google_vision_api.GoogleVisionAPI}
# Maps recognition provider names to an object of the provider.

def _validate_args(args):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    if bool(args.input_ingestion_pipelinerun_id) == bool(args.input_ingestion_provider):
        raise ValueError('pipeline requires exactly one of out of ingestion pipeline run \
            and ingestion provider - zero or two were given')
    if args.input_ingestion_pipelinerun_id and not isinstance(args.input_ingestion_pipelinerun_id, str):
        raise ValueError('ingestion pipeline run id is not a string')
    if args.input_ingestion_provider and not isinstance(args.input_ingestion_provider, str):
        raise ValueError('ingestion pipeline provider id is not a string')
    if not isinstance(args.input_recognition_provider, str):
        raise ValueError('recognition provider is not a string')

def run(argv=None):
    """Main entry point, defines and runs the image recognition pipeline.
    
    Input: either ingestion run id or ingestion provider id.
    The input is used for querying the database for image ingested by
    either one of the optional inputs.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input-ingestion-pipelinerun-id',
        dest='input_ingestion_pipelinerun_id',
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
        required = False, # Optional - only for development reasons.
        help='Output file to write results to for testing.')
    known_args, pipeline_args = parser.parse_known_args(argv)
    _validate_args(known_args)
    ingestion_run = known_args.input_ingestion_pipelinerun_id
    ingestion_provider = known_args.input_ingestion_provider
    recognition_provider = get_provider(known_args.input_recognition_provider, NAME_TO_PROVIDER)
    # Creating an object of type ImageRecognitionProvider
    # for the specific image recognition provider input.
    job_name = 'RECOGNITION-{time_id}-{recognition_provider}'.format(time_id = get_timestamp_id(),\
        recognition_provider = recognition_provider.provider_id.replace('-','').upper())
    pipeline_options = PipelineOptions(pipeline_args, job_name=job_name)

    with beam.Pipeline(options=pipeline_options) as pipeline:
        indices_for_batching = pipeline | 'create' >> beam.Create([i for i in range(10)])
        if ingestion_run:
            # If the input was for specifing the images dataset was an ingestion run.
            dataset = indices_for_batching | 'get images dataset' >> \
                beam.ParDo(GetBatchedImageDataset(), ingestion_run=ingestion_run)
        else:
            # If the input was for specifing the images dataset was an ingestion provider.
            dataset = indices_for_batching | 'get images dataset' >> \
                beam.ParDo(GetBatchedImageDataset(), ingestion_provider=ingestion_provider)
        filtered_dataset = dataset | 'filter images' >> \
            beam.Filter(recognition_provider.is_eligible)
        images_batch = filtered_dataset | 'combine to batches' >> \
            beam.GroupBy(lambda doc: int(doc['random']*100)) |\
                beam.ParDo(lambda element: [element[1]])
        labelled_images_batch = images_batch | 'label by batch' >> \
            beam.ParDo(recognition_provider)
            # Labels the images by the process method of the provider.
        labelled_images = labelled_images_batch | \
            beam.FlatMap(lambda elements: elements)
        redefine_map = get_redefine_map(recognition_provider.provider_id)
        labels_id = labelled_images | 'redefine labels' >> \
            beam.ParDo(RedefineLabels(), redefine_map)
        # pylint: disable=expression-not-assigned
        # labels_id | 'upload' >> beam.ParDo(StoreInDatabase(), job_name, recognition_provider.provider_id)
        # if ingestion_run:
        #     send_email_to_notify_admins(job_name=job_name, ingestion_run=ingestion_run)
        # else:
        #     send_email_to_notify_admins(job_name=job_name, ingestion_provider=ingestion_provider)

        if known_args.output: # For testing.
            def format_result(image, labels):
                return '%s: %s' % (image['url'], labels)
            output = labels_id | 'Format' >> beam.MapTuple(format_result)
            output | 'Write' >> WriteToText(known_args.output)
    upload_to_pipeline_runs_collection(recognition_provider.provider_id, job_name)
    # TODO: add access to job id with dataflow
    # print(DataflowApplicationClient(pipeline_options).job_id_for_name(job_name))
    
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
