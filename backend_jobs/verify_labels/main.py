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

A verify labels pipeline to verify the labels recognized by a specific provider
or by a specific run.

The pipeline uses Python's Apache beam library to parallelize the different stages.
The labels are taken from a Firestore database using a query and are change to visible.
The pipeline updates COLLECTION_IMAGES to make sure all visible labels appear
for each image in the database.
"""

from __future__ import absolute_import

import argparse
import logging
import apache_beam as beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions

from backend_jobs.verify_labels.pipeline_lib.redefine_labels import RedefineLabels, get_redefine_map
from backend_jobs.verify_labels.pipeline_lib.firestore_database import GetBatchedLabelsDataset,\
    UpdateDatabaseWithVisibleLabels, update_pipelinerun_doc_to_visible, get_provider_id_from_run_id
from backend_jobs.pipeline_utils.utils import generate_cloud_dataflow_job_name, create_query_indices
from backend_jobs.pipeline_utils.firestore_database import store_pipeline_run,\
    update_pipeline_run_when_failed, update_pipeline_run_when_succeeded, UpdateHeatmapDatabaseAfterVerification

_PIPELINE_TYPE = 'verify_labels'

def _validate_args(input_recognition_run_id):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    if not isinstance(input_recognition_run_id, str):
        raise ValueError('recognition pipeline run id is not a string')

def parse_arguments():
     # Using external parser: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input-recognition-run',
        dest='input_recognition_run_id',
        required=True,
        help='Input of recognition pipeline run for labels dataset.')
    parser.add_argument(
        '--output',
        dest='output',
        required = False, # Optional - only for development reasons.
        help='Output file to write results to for testing.')
    return parser.parse_known_args()

def run(recognition_run, output=None, run_locally=False):
    """Main entry point, defines and runs the verify labels pipeline.

    Input: recognition run id.
    The input is used for querying the database for labels recognized by the
    input run and verifying them.
    
    """
    _validate_args(recognition_run)
    job_name = generate_cloud_dataflow_job_name(_PIPELINE_TYPE, recognition_run)
    
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
            dataset = indices_for_batching | 'get labels dataset' >> \
                beam.ParDo(GetBatchedLabelsDataset(), recognition_run)
            provider_id = get_provider_id_from_run_id(recognition_run)
            redefine_map = get_redefine_map(provider_id)
            redefine_labels = dataset | 'redefine labels' >> \
                beam.ParDo(RedefineLabels(), redefine_map)
            new_point_keys = redefine_labels | 'update database and get new point keys' >>\
                beam.ParDo(UpdateDatabaseWithVisibleLabels())
            update_pipelinerun_doc_to_visible(recognition_run)
            new_point_keys_and_sum = new_point_keys | 'combine all point keys' >> \
                    beam.CombinePerKey(sum)
            # pylint: disable=expression-not-assigned
            new_point_keys_and_sum | 'update heatmap database' >> beam.ParDo(UpdateHeatmapDatabaseAfterVerification())

            if output: # For testing.
                # pylint: disable=expression-not-assigned
                redefine_labels | 'Write' >> WriteToText(output)
        update_pipeline_run_when_succeeded(job_name)
    except:
        update_pipeline_run_when_failed(job_name)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    args, pipeline_args = parse_arguments()
    run(args.input_recognition_run_id, args.output, run_locally=True)
