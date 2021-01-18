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

A recognition removal pipeline to remove all labels recognized by a specific provider
or by a specific run.

The pipeline uses Python's Apache beam library to parallelize the different stages.
The labels are taken from a Firestore database using a query
and are then deleted from the databse.
The pipeline updates COLLECTION_IMAGES to make sure only existing labels are left
for each image in the database.
"""

from __future__ import absolute_import

import argparse
import logging

import apache_beam as beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions

from backend_jobs.pipeline_utils.utils import generate_cloud_dataflow_job_name, create_query_indices
from backend_jobs.pipeline_utils.firestore_database import store_pipeline_run,\
    update_pipeline_run_when_succeeded, update_pipeline_run_when_failed
from backend_jobs.recognition_removal.pipeline_lib.firestore_database import\
    GetAndDeleteBatchedLabelsDataset, UpdateLabelsInImageDocs, update_pipelinerun_doc_to_invisible
from backend_jobs.pipeline_utils.firestore_database import UpdateHeatmapDatabaseAfterRemoval

_PIPELINE_TYPE = 'recognition_removal'

def _validate_args(input_recognition_run_id, input_recognition_provider):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    if bool(input_recognition_run_id) == bool(input_recognition_provider):
        raise ValueError('pipeline requires exactly one of out of recognition pipeline run \
            and recognition provider - zero or two were given')
    if input_recognition_run_id and\
        not isinstance(input_recognition_run_id, str):
        raise ValueError('recognition pipeline run id is not a string')
    if input_recognition_provider and not isinstance(input_recognition_provider, str):
        raise ValueError('recognition pipeline provider id is not a string')

def parse_arguments():
    # Using external parser: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input-recognition-run',
        dest='input_recognition_run_id',
        help='Input of recognition pipeline run for the labels tht should be removed.')
    parser.add_argument(
        '--input-recognition-provider',
        dest='input_recognition_provider',
        help='Input of recognition pipeline provider for labels that should be removed.')
    parser.add_argument(
        '--output',
        dest='output',
        required = False, # Optional - only for development reasons.
        help='Output file to write results to for testing.')
    return parser.parse_known_args()

def run(recognition_run=None, recognition_provider=None, output=None, run_locally=False):
    """Main entry point, defines and runs the labels removal pipeline.

    Input: either recognition run id or recognition provider id.
    The input is used for querying the database for labels recognized by
    either one of the optional inputs.
    
    """
    _validate_args(recognition_run, recognition_provider)
    if recognition_run:
        job_name = generate_cloud_dataflow_job_name(_PIPELINE_TYPE, recognition_run)
    else:
        job_name = generate_cloud_dataflow_job_name(_PIPELINE_TYPE, recognition_provider)

    if run_locally:
        pipeline_options = PipelineOptions()
    else:
        output = 'gs://demo-bucket-step/results/outputs'
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
            store_pipeline_run(job_name)
            indices_for_batching = pipeline | 'create' >> beam.Create(create_query_indices())
            dataset = indices_for_batching | 'get labels dataset and delete Firebase docs' >> \
                beam.ParDo(GetAndDeleteBatchedLabelsDataset(),\
                    recognition_provider=recognition_provider, recognition_run=recognition_run)
            if recognition_run:
                update_pipelinerun_doc_to_invisible(recognition_run)
            dataset_group_by_parent_image = dataset | 'group all labels by parent image' >>\
                beam.GroupByKey()
            deleted_point_keys = dataset_group_by_parent_image | 'update database and get point keys' >>\
                beam.ParDo(UpdateLabelsInImageDocs())
            deleted_point_keys_and_sum = deleted_point_keys | 'combine all point keys' >> \
                    beam.CombinePerKey(sum)
            # pylint: disable=expression-not-assigned
            deleted_point_keys_and_sum | 'update heatmap database' >> beam.ParDo(UpdateHeatmapDatabaseAfterRemoval())

            if output: # For testing.
                # pylint: disable=expression-not-assigned
                dataset_group_by_parent_image | 'Write' >> WriteToText(output)
            
        update_pipeline_run_when_succeeded(job_name)
    except:
        update_pipeline_run_when_failed(job_name)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    args, pipeline_args = parse_arguments()
    run(args.input_recognition_run_id, args.input_recognition_provider, args.output,\
        run_locally=True)
