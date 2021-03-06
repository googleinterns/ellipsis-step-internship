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
from backend_jobs.pipeline_utils.firestore_database import \
    update_pipeline_run_when_failed, update_pipeline_run_when_succeeded, store_pipeline_run
from backend_jobs.pipeline_utils.utils import generate_cloud_dataflow_job_name, create_query_indices
from backend_jobs.recognition_pipeline.providers.providers import get_recognition_provider

_PIPELINE_TYPE = 'recognition'

def _validate_args(recognition_provider, ingestion_pipelinerun_id, ingestion_provider):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    if bool(ingestion_pipelinerun_id) == bool(ingestion_provider):
        raise ValueError('pipeline requires exactly one of out of ingestion pipeline run \
            and ingestion provider - zero or two were given')
    if ingestion_pipelinerun_id and\
        not isinstance(ingestion_pipelinerun_id, str):
        raise ValueError('ingestion pipeline run id is not a string')
    if ingestion_provider and not isinstance(ingestion_provider, str):
        raise ValueError('ingestion pipeline provider id is not a string')
    if not isinstance(recognition_provider, str):
        raise ValueError('recognition provider is not a string')

def parse_arguments():
    # Using external parser: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input-ingestion-run-id',
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
        required=False,  # Optional - only for development reasons.
        help='Output file to write results to for testing.')
    return parser.parse_known_args()


def run(recognition_provider_name, ingestion_run=None, ingestion_provider=None, output_name=None, run_locally=False):
    """Main entry point, defines and runs the image recognition pipeline.

    Input: either ingestion run id or ingestion provider id.
    The input is used for querying the database for image ingested by
    either one of the optional inputs.
    """
    _validate_args(recognition_provider_name, ingestion_run, ingestion_provider)
    recognition_provider = get_recognition_provider(recognition_provider_name)
    job_name = generate_cloud_dataflow_job_name(_PIPELINE_TYPE, recognition_provider.provider_id)
    if run_locally:
        pipeline_options = PipelineOptions()
    else:
        output_name = 'gs://demo-bucket-step/results/outputs'
        pipeline_options = PipelineOptions(
            flags=None,
            runner='DataflowRunner',
            project='step-project-ellispis',
            job_name=job_name,
            temp_location='gs://demo-bucket-step/temp',
            region='europe-west2',
            setup_file='./setup.py',
        )
    
    try:
        with beam.Pipeline(options=pipeline_options) as pipeline:
            store_pipeline_run(job_name, recognition_provider.provider_id)
            indices_for_batching = pipeline | 'create' >> beam.Create(create_query_indices())
            if ingestion_run:
                dataset = indices_for_batching | 'get images dataset' >> \
                    beam.ParDo(GetBatchedImageDataset(), ingestion_run=ingestion_run)
            else:
                dataset = indices_for_batching | 'get images dataset' >> \
                    beam.ParDo(GetBatchedImageDataset(), ingestion_provider=ingestion_provider)
            dataset_with_url_for_provider = dataset | 'add url for labeling' >> \
                beam.ParDo(recognition_provider.add_url_for_recognition_api)
            filtered_dataset = dataset_with_url_for_provider | 'filter images' >> \
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

            if output_name: # For testing.
                def format_result(image, labels):
                    return '%s: %s' % (image['url'], labels)
                output = labeled_images | 'Format' >> beam.MapTuple(format_result)
                output | 'Write' >> WriteToText(output_name)
        update_pipeline_run_when_succeeded(job_name)
    except:
        update_pipeline_run_when_failed(job_name)
        raise


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    args, pipeline_args = parse_arguments()
    run(args.input_recognition_provider, args.input_ingestion_pipelinerun_id, args.input_ingestion_provider, args.output, run_locally=True)
