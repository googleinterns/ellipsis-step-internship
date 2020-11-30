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

from backend_jobs.verify_labels.pipeline_lib.firestore_database import GetDataset,\
    UpdateDatabase, update_pipelinerun_doc_to_visible, get_provider_id_from_run_id
from backend_jobs.pipeline_utils.utils import generate_job_name

_PIPELINE_TYPE = 'verify_images'


def _validate_args(args):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    if not isinstance(args.input_recognition_run_id, str):
        raise ValueError('recognition pipeline run id is not a string')


def run(argv=None):
    """Main entry point, defines and runs the verifymor labels pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_pipeline_run',
        dest='input_pipeline_run',
        help='Input of pipeline run for ingested images.')
    parser.add_argument(
        '--input_image_provider',
        dest='input_image_provider',
        help='Input of provider for ingested images.')
    parser.add_argument(
        '--output',
        dest='output',
        help='Output file to write results to for testing.')
    known_args, pipeline_args = parser.parse_known_args(argv)
    _validate_args(known_args)

    # pipeline_run = known_args.input_pipeline_run
    input_image_provider = known_args.input_image_provider

    if input_image_provider:
        job_name = generate_job_name(_PIPELINE_TYPE, 'input_image_provider')
    else:
        job_name = generate_job_name(_PIPELINE_TYPE, 'pipeline_run')

    pipeline_options = PipelineOptions(pipeline_args, job_name=job_name)

    with beam.Pipeline(options=pipeline_options) as pipeline:
        indices_for_batching = pipeline | 'create' >> beam.Create([i for i in range(10)])
        dataset = indices_for_batching | 'get dataset' >> beam.ParDo(GetDataset(), input_image_provider)
        # pylint: disable=expression-not-assigned
        dataset | 'update visibility database' >> beam.ParDo(UpdateVisibilityInDatabase())
        update_pipelinerun_doc_to_visible(input_image_provider)

        if known_args.output:  # For testing.
            # pylint: disable=expression-not-assigned
            input_image_provider | 'Write' >> WriteToText(known_args.output)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
