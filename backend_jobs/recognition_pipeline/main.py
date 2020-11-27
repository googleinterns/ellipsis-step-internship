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

import apache_beam as beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from backend_jobs.recognition_pipeline.pipeline_lib.firestore_database import\
    GetBatchedImageDataset, UpdateImageLabelsInDatabase
from backend_jobs.pipeline_utils.firestore_database import store_pipeline_run
from backend_jobs.pipeline_utils.utils import generate_cloud_dataflow_job_name
from backend_jobs.recognition_pipeline.providers.providers import get_recognition_provider

_PIPELINE_TYPE = 'recognition'

def _validate_args(args):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    if bool(args.input_ingestion_pipelinerun_id) == bool(args.input_ingestion_provider):
        raise ValueError('pipeline requires exactly one of out of ingestion pipeline run \
            and ingestion provider - zero or two were given')
    if args.input_ingestion_pipelinerun_id and\
        not isinstance(args.input_ingestion_pipelinerun_id, str):
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
    # Using external parser: https://docs.python.org/3/library/argparse.html
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
    # Creating an object of type ImageRecognitionProvider
    # for the specific image recognition provider input.
    recognition_provider = get_recognition_provider(known_args.input_recognition_provider)
    job_name = generate_cloud_dataflow_job_name(_PIPELINE_TYPE, recognition_provider)
    pipeline_options = PipelineOptions(pipeline_args, job_name=job_name)

    with beam.Pipeline(options=pipeline_options) as pipeline:
        indices_for_batching = pipeline | 'create' >> beam.Create([i for i in range(10)])
        if ingestion_run:
            dataset = indices_for_batching | 'get images dataset' >> \
                beam.ParDo(GetBatchedImageDataset(), ingestion_run=ingestion_run)
        else:
            dataset = indices_for_batching | 'get images dataset' >> \
                beam.ParDo(GetBatchedImageDataset(), ingestion_provider=ingestion_provider)
        filtered_dataset = dataset | 'filter images' >> \
            beam.Filter(recognition_provider.is_eligible)
        images_batch = filtered_dataset | 'combine to batches' >> \
            beam.GroupBy(lambda doc: int(doc['random']*100)) |\
                beam.ParDo(lambda element: [element[1]])
        # Labels the images by the process method of the provider.
        labeled_images_batch = images_batch | 'label by batch' >> \
            beam.ParDo(recognition_provider)
        labeled_images = labeled_images_batch | \
            beam.FlatMap(lambda elements: elements)
        # pylint: disable=expression-not-assigned
        labeled_images | 'store in database' >> beam.ParDo(UpdateImageLabelsInDatabase(),\
            job_name, recognition_provider.provider_id)

        if known_args.output: # For testing.
            def format_result(image, labels):
                return '%s: %s' % (image['url'], labels)
            output = labeled_images | 'Format' >> beam.MapTuple(format_result)
            output | 'Write' >> WriteToText(known_args.output)
    store_pipeline_run(recognition_provider.provider_id, job_name)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
