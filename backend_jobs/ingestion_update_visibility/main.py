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

An update visibility pipeline to update the visibility in documents/images from specific dataset
by a specific provider/ pipeline run.

The pipeline uses Python's Apache beam library to parallelize the different stages.
The images are taken from a Firestore database.
"""

from __future__ import absolute_import

import argparse
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

from backend_jobs.ingestion_update_visibility.pipeline_lib.firestore_database import GetDataset
from backend_jobs.ingestion_update_visibility.pipeline_lib.firestore_database import UpdateVisibilityInDatabase
from backend_jobs.ingestion_update_visibilityss.pipeline_lib.firestore_database import update_pipelinerun_doc_to_visible
from backend_jobs.pipeline_utils.utils import generate_cloud_dataflow_job_name
from backend_jobs.pipeline_utils.data_types import VisibilityType


_PIPELINE_TYPE = 'update_visibility_pipeline'


def _validate_args(args):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    if args.input_pipeline_run is not None and args.input_image_provider is not None:
        raise ValueError('input can only be or input_image_provider or input_image_provider')
    if args.input_pipeline_run is None and args.input_image_provider is None:
        raise ValueError('missing input e.g. input_image_provider/input_image_provider')
    if not isinstance(args.input_pipeline_run, str) and args.input_pipeline_run:
        raise ValueError('pipeline run id is not a string')
    if not isinstance(args.input_image_provider, str) and args.input_image_provider:
        raise ValueError('image provider is not a string')


def _get_visibility(visibility):
    """ Converts the given visibility(string) to VisibilityType.
    If the visibility is not a valid string- throws an error.

    """
    if visibility == 'VISIBLE':
        return VisibilityType.VISIBLE
    if visibility == 'INVISIBLE':
        return VisibilityType.INVISIBLE
    raise ValueError('missing input_visibility can be VISIBLE/INVISIBLE')


def run(argv=None):
    """Main entry point, defines and runs the updating visibility pipeline."""
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
        default=VisibilityType.VISIBLE,
        help='Input of provider for ingested images.')
    known_args, pipeline_args = parser.parse_known_args(argv)
    _validate_args(known_args)

    pipeline_run = known_args.input_pipeline_run
    image_provider = known_args.input_image_provider
    visibility = _get_visibility(known_args.input_visibility)

    if image_provider:
        job_name = generate_cloud_dataflow_job_name(_PIPELINE_TYPE, image_provider)
    else:
        job_name = generate_cloud_dataflow_job_name(_PIPELINE_TYPE, pipeline_run)

    pipeline_options = PipelineOptions(pipeline_args, job_name=job_name)

    with beam.Pipeline(options=pipeline_options) as pipeline:
        indices_for_batching = pipeline | 'create' >> beam.Create([i for i in range(10)])
        dataset = indices_for_batching | 'get dataset' >>\
            beam.ParDo(GetDataset(), image_provider=image_provider, pipeline_run=pipeline_run)
        dataset | 'update visibility database' >>\
            beam.ParDo(UpdateVisibilityInDatabase(), visibility)
        update_pipelinerun_doc_to_visible(image_provider)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
