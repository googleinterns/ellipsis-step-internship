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
from backend_jobs.pipeline_utils import utils
from backend_jobs.pipeline_utils import providers




def _generate_image_id(image):
    print(image.url)
    hash_url = hashlib.sha1(image.url.encode())
    hex_dig_id = hash_url.hexdigest()
    image.image_id = hex_dig_id
    return image

def _validate_args(args):
    """ Checks whether the pipeline's arguments are valid.
    If not - throws an error.

    """
    if not isinstance(args.input_provider_name, str):
        raise ValueError('ingestion provider is not a string')

def _is_valid_image(image):
    """ This function returns whether the given image satisfies minimum requirements of the platform
    e.g. url != none
    """
    return image.url  and \
        image.latitude and \
        image.longitude and \
        image.format and \
        image.width_pixels > 100 and \
        image.height_pixels > 100

def run(argv=None):
    """ Main entry point; defines and runs the image ingestion pipeline.
    """
    # Using external parser: https://docs.python.org/3/library/argparse.html 
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_provider_name',
        dest = 'input_provider_name',
        default = 'FlickrProvider',
        help = 'Provider name to process.')
    parser.add_argument(
        '--input_provider_args',
        dest = 'input_provider_args',
        default = '',
        help = 'args to query by provider.')
    parser.add_argument(
        '--output',
        dest = 'output',
        required = False, # Optional - only for development reasons.
        help = 'Output file to write results to.')

    known_args, pipeline_args = parser.parse_known_args(argv)
    _validate_args(known_args)
    image_provider = utils.get_provider(
        providers.IMAGE_PROVIDERS,
        known_args.input_provider_name,
        known_args.input_provider_args)

    if not image_provider.enabled:
        raise ValueError('ingestion provider is not enabled')

    job_name = 'ingestion-' + utils.get_timestamp_id()
    pipeline_options = PipelineOptions(pipeline_args, job_name=job_name)

    # The pipeline will be run on exiting the with block.
    # pylint: disable=expression-not-assigned
    with apache_beam.Pipeline(options=pipeline_options) as pipeline:

        num_of_pages = image_provider.get_num_of_pages()
        create_batch = (pipeline | 'create' >> \
            apache_beam.Create([i for i in range(1, int(3)+1)]))
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

        if known_args.output:
            generate_image_id | 'Write' >> WriteToText(known_args.output)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
