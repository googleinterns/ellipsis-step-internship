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
 """

from __future__ import absolute_import
import argparse
import logging
import hashlib
import apache_beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from backend_jobs.ingestion_pipeline.pipeline_lib import firestore_database
from backend_jobs.ingestion_pipeline.providers import providers
from backend_jobs.pipeline_utils.firestore_database import store_pipeline_run,\
    update_pipeline_run_when_failed, update_pipeline_run_when_succeeded
from backend_jobs.pipeline_utils import utils


def _generate_image_id(image):
    """ This function gets an image and updates the id to be the hashed url.

    Args:
        image: Type ImageAttributes.

    Returns:
        image: Type ImageAttributes with an updated unique id.
    """
    hash_url = hashlib.sha1(image.url.encode())
    hex_hash_id = hash_url.hexdigest()
    image.image_id = hex_hash_id
    return image


def _validate_args(input_provider_name):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    if not isinstance(input_provider_name, str):
        raise ValueError('ingestion provider is not a string')


def _is_valid_image(image):
    """ This function returns whether the given image satisfies minimum requirements of the platform
    e.g. url != none
    """
    return \
        image.url and \
        image.latitude and \
        image.longitude and \
        image.format and \
        image.width_pixels > 100 and \
        image.height_pixels > 100


def parse_arguments():
    # Using external parser: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_provider_name',
        dest='input_provider_name',
        default='FlickrProvider-2020',
        help='Provider name to process.')
    parser.add_argument(
        '--input_provider_args',
        dest='input_provider_args',
        default=None,
        help='args to query by provider.')
    parser.add_argument(
        '--output',
        dest='output',
        required=False,  # Optional - only for development reasons.
        help='Output file to write results to.')
    return parser.parse_known_args()


def run(input_provider_name, input_provider_args=None, output_name=None, run_locally=False):
    """Main entry point,  defines and runs the image ingestion pipeline.

    Input:
        input_provider_name- the image provider to ingest images from.
        input_provider_args- optional query to pass to the image provider.
        e.g 'tags:cat,dog-tag_mode:any'.

        Additional parameters that are being forwarded to the PipelineOptions:
        region- The rigion the job runs, e.g. europe-west2.
        output- Where to save the outpot, e.g. outputs.txt.
        runner- The runner of the job, e.g. DataflowRunner.
        project- Project id, e.g. step-project-ellispis.
        requirements_file- A file with all externall imports, e.g. requirements.txt.
        extra_package- A zip file with all internal import packages,
        e.g. pipeline-BACKEND_JOBS-0.0.1.tar.gz.
    """
    _validate_args(input_provider_name)
    image_provider = providers.get_provider(
        providers.IMAGE_PROVIDERS,
        input_provider_name,
        input_provider_args)

    if not image_provider.enabled:
        raise ValueError('ingestion provider is not enabled')

    job_name = utils.generate_cloud_dataflow_job_name('ingestion', image_provider.provider_id)
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
    store_pipeline_run(image_provider.provider_id, job_name)
    try:
        # The pipeline will be run on exiting the with block.
        # pylint: disable=expression-not-assigned
        with apache_beam.Pipeline(options=pipeline_options) as pipeline:

            num_of_pages = image_provider.get_num_of_pages()
            create_batch = pipeline | 'create' >> \
                apache_beam.Create([i for i in range(1, int(num_of_pages)+1)])
            images = create_batch | 'call API' >> \
                apache_beam.ParDo(image_provider.get_images)
            extracted_elements = images | 'extract attributes' >> \
                apache_beam.Map(image_provider.get_image_attributes)
            filtered_elements = extracted_elements | 'filter' >> \
                apache_beam.Filter(_is_valid_image)
            generate_image_id = filtered_elements | 'generate image id' >> \
                apache_beam.Map(_generate_image_id)

            generate_image_id | 'store_image' >> \
                apache_beam.ParDo(firestore_database.AddOrUpdateImageDoFn(), image_provider, job_name)

            if output_name:
                generate_image_id | 'Write' >> WriteToText(output_name)

        update_pipeline_run_when_succeeded(job_name)
    except:
        update_pipeline_run_when_failed(job_name)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    args, pipeline_args = parse_arguments()
    run(args.input_provider_name, args.input_provider_args, args.output, run_locally=True)
