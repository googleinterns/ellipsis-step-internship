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

A pipeline to update the visibility in documents/images from a specific dataset
by a specific provider/ pipeline run.

The pipeline uses Python's Apache beam library to parallelize the different stages.
The images are taken from a Firestore database.
"""

from __future__ import absolute_import

import argparse
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

from backend_jobs.ingestion_update_visibility.pipeline_lib import firestore_database 
from backend_jobs.pipeline_utils.utils import generate_cloud_dataflow_job_name
from backend_jobs.pipeline_utils.data_types import VisibilityType
from backend_jobs.pipeline_utils import constants


_PIPELINE_TYPE = 'update_visibility_pipeline'


def _validate_args(input_image_provider, input_pipeline_run):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    if input_pipeline_run is not None and input_image_provider is not None:
        raise ValueError('Input can only be or input_image_provider or input_pipeline_run')
    if input_pipeline_run is None and input_image_provider is None:
        raise ValueError('Missing input e.g. input_image_provider/input_pipeline_run')
    if not isinstance(input_pipeline_run, str) and input_pipeline_run:
        raise ValueError('Pipeline run id is not a string')
    if not isinstance(input_image_provider, str) and input_image_provider:
        raise ValueError('Image provider is not a string')


def _get_visibility(visibility):
    """ Converts the given visibility(string) to VisibilityType.
    If the visibility is not a valid string- throws an error.

    """
    if visibility == 'VISIBLE':
        return VisibilityType.VISIBLE
    if visibility == 'INVISIBLE':
        return VisibilityType.INVISIBLE
    raise ValueError('Missing input_visibility can be VISIBLE/INVISIBLE')



def parse_arguments():
    # Using external parser: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_pipeline_run',
        dest='input_pipeline_run',
        default=None,
        help='Input of pipeline run for ingested images.')
    parser.add_argument(
        '--input_image_provider',
        dest='input_image_provider',
        default=None,
        help='Input of provider for ingested images.')
    parser.add_argument(
        '--input_visibility',
        dest='input_visibility',
        default='VISIBLE',
        help='Input visibility to update to.')
    return parser.parse_known_args()


def run(input_image_provider=None, input_pipeline_run=None, input_visibility=None, run_locally=False):
    """Main entry point, defines and runs the updating visibility pipeline."""
    _validate_args(input_image_provider, input_pipeline_run)
    pipeline_run = input_pipeline_run
    image_provider = input_image_provider
    visibility = _get_visibility(input_visibility)

    if image_provider:
        job_name = generate_cloud_dataflow_job_name(_PIPELINE_TYPE, image_provider)
    else:
        job_name = generate_cloud_dataflow_job_name(_PIPELINE_TYPE, pipeline_run)

    if run_locally:
        pipeline_options = PipelineOptions()
    else:
        pipeline_options = PipelineOptions(
            flags=None,
            runner='DataflowRunner',
            project='step-project-ellispis',
            job_name=job_name,
            temp_location='gs://demo-bucket-step/temp',
            region='europe-west2',
        )

    with beam.Pipeline(options=pipeline_options) as pipeline:
        indices_for_batching = pipeline | 'create' >> beam.Create(constants.LIST_FOR_BATCHES)
        dataset = indices_for_batching | 'get dataset' >>\
            beam.ParDo(firestore_database.GetDataset(
                image_provider=image_provider, pipeline_run=pipeline_run))
        dataset_group_by_parent_image = dataset | 'group all by parent image' >>\
            beam.GroupByKey()
        updated_subcollection = dataset_group_by_parent_image | 'update visibility subcollection' >>\
            beam.ParDo(firestore_database.UpdateVisibilityInDatabaseSubcollection(
                image_provider=image_provider, pipeline_run=pipeline_run),
                visibility)
        updated_subcollection | 'update visibility collection' >>\
            beam.ParDo(firestore_database.UpdateVisibilityInDatabaseCollection(
                image_provider=image_provider, pipeline_run=pipeline_run))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    args, pipeline_args = parse_arguments()
    run(args.input_image_provider, args.input_pipeline_run, args.input_visibility, run_locally=True)
