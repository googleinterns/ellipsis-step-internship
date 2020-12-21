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

A heatmap aggregation pipeline to aggregate coordinates into weighted points.

The pipeline uses Python's Apache beam library to parallelize the different stages.
The images are taken from COLLECTION_IMAGES in the project's firestore database.
The pipeline updates COLLECTION_HEATMAP to make sure all vertified images and labels are
counted for the frontend's heatmap.
"""

from __future__ import absolute_import

import argparse
import logging
import apache_beam as beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions

from backend_jobs.heatmap_aggregation.pipeline_lib.firestore_database import\
    GetPointKeysByBatch, UpdateHeatmapDatabase
from backend_jobs.pipeline_utils.utils import generate_cloud_dataflow_job_name, create_query_indices
from backend_jobs.pipeline_utils.firestore_database import store_pipeline_run, \
    update_pipeline_run_when_failed, update_pipeline_run_when_succeeded

_PIPELINE_TYPE = 'heatmap_aggreation'

def parse_arguments():
    # Using external parser: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output',
        dest='output',
        required = False, # Optional - only for development reasons.
        help='Output file to write results to for testing.')
    return parser.parse_known_args()

def run(output=None, run_locally=False):
    """Main entry point, runs the heatmap aggregation pipeline.

    """
    if not output:
        raise ValueError('hi')
    job_name = generate_cloud_dataflow_job_name(_PIPELINE_TYPE, 'all images') #TODO: change additional info.
    
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
    
    store_pipeline_run(job_name)
    try:
        with beam.Pipeline(options=pipeline_options) as pipeline:
            indices_for_batching = pipeline | 'create' >> beam.Create(create_query_indices())
            point_keys = indices_for_batching | 'get point keys' >> \
                beam.ParDo(GetPointKeysByBatch())
            point_keys_and_sum = point_keys | 'combine all point keys' >> \
                beam.CombinePerKey(sum)
            # pylint: disable=expression-not-assigned
            point_keys | 'update database' >> beam.ParDo(UpdateHeatmapDatabase())

            if output: # For testing.
                # pylint: disable=expression-not-assigned
                point_keys_and_sum | 'Write' >> WriteToText(output)

        update_pipeline_run_when_succeeded(job_name)
    except:
        update_pipeline_run_when_failed(job_name)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    args, pipeline_args = parse_arguments()
    run(args.output, run_locally=True)
