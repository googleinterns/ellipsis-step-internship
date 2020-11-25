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

from backend_jobs.pipeline_utils.firestore_database import initialize_db
from backend_jobs.recognition_pipeline.pipeline_lib.firestore_database import add_id_to_dict
from backend_jobs.pipeline_utils.utils import generate_job_name
from backend_jobs.removal_pipeline.pipeline_lib.firestore_database import GetBatchedDataset, UpdateLabelsInImageDocs
    
def _validate_args(args):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    return True
    if bool(args.input_recognition_run_id) == bool(args.input_recognition_provider):
        raise ValueError('pipeline requires exactly one of out of recognition pipeline run \
            and recognition provider - zero or two were given')
    if args.input_recognition_run_id and\
        not isinstance(args.input_recognition_run_id, str):
        raise ValueError('recognition pipeline run id is not a string')
    if args.input_recognition_provider and not isinstance(args.input_recognition_provider, str):
        raise ValueError('recognition pipeline provider id is not a string')


def run(argv=None):
    """Main entry point, defines and runs the image recognition pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_pipeline_run',
        dest='input_pipeline_run',
        help='Input of recognition pipeline run for the labels tht should be removed.')
    parser.add_argument(
        '--input_provider',
        dest='input_provider',
        help='Input of recognition pipeline provider for labels that should be removed.')
    parser.add_argument(
        '--output',
        dest='output',
        help='Output file to write results to for testing.')
    known_args, pipeline_args = parser.parse_known_args(argv)
    _validate_args(known_args)
    pipeline_run = known_args.input_pipeline_run
    provider = known_args.input_provider
    if pipeline_run:
        job_name = generate_job_name('remove', pipeline_run)
    else:
        print(provider)
        job_name = generate_job_name('remove', provider)

    pipeline_options = PipelineOptions(pipeline_args, job_name=job_name)

    with beam.Pipeline(options=pipeline_options) as pipeline:

        indices_for_batching = pipeline | 'create' >> beam.Create([i for i in range(10)])

        if provider:
            dataset = indices_for_batching | 'get labels dataset' >> \
                beam.ParDo(GetBatchedDataset(), provider=provider)
        else:
            dataset = indices_for_batching | 'get labels dataset' >> \
                beam.ParDo(GetBatchedDataset(), pipeline_run=pipeline_run)

        #dataset | 'update database' >> beam.ParDo(UpdateLabelsInImageDocs())
        #if known_args.output: # For testing.
        #    dataset | 'Write' >> WriteToText(known_args.output)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
