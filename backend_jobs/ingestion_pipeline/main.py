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
import apache_beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from backend_jobs.ingestion_pipeline.providers import image_provider_flickr
from backend_jobs.ingestion_pipeline.pipeline_lib import firestore_database
from backend_jobs.pipeline_utils import utils


#This map provides all the Providers.ImageProviders in the platform
IMAGE_PROVIDERS = {'FlickrProvider': image_provider_flickr.FlickrProvider}

def is_valid_image(image):
    """
    This function returns whether the given image satisfies minimum requirements of the platform
     e.g.:; url != none
    """
    return image.url  and \
        image.coordinates and \
        image.format and \
        image.resolution['width'] > 100 and \
        image.resolution['height'] > 100

def run(argv=None):
    """
    Main entry point; defines and runs the image ingestion pipeline.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_provider_name',
        dest = 'input_provider_name',
        default = 'FlickrProvider',
        help = 'Provider name to process.')
    parser.add_argument(
        '--input_provider_args',
        dest = 'input_provider_args',
        default = 'all',
        help = 'label to query by.')
    parser.add_argument(
        '--output',
        dest = 'output',
        help = 'Output file to write results to.')
    known_args, pipeline_args = parser.parse_known_args(argv)
    job_name = 'ingestion-' + utils.get_timestamp_id()
    pipeline_options = PipelineOptions(pipeline_args, job_name=job_name)

    # The pipeline will be run on exiting the with block.
    # pylint: disable=expression-not-assigned
    with apache_beam.Pipeline(options=pipeline_options) as pipeline:

        image_provider = utils.get_provider(known_args.input_provider_name, _IMAGE_PROVIDERS)
        query_by_arguments_map = {'tag':known_args.input_provider_args}
        num_of_batches = image_provider.get_num_of_pages(query_by_arguments_map)
        create_batch = (pipeline | 'create' >> \
            apache_beam.Create([i for i in range(1, int(num_of_batches)+1)]) )
        images = create_batch | 'call API' >> \
            apache_beam.ParDo(image_provider.get_images, query_by_arguments_map)
        extracted_elements = images | 'extract attributes' >> \
            apache_beam.Map(image_provider.get_image_attributes)
        filtered_elements = extracted_elements | 'filter' >> \
            apache_beam.Filter(is_valid_image)
        filtered_elements | 'upload' >> \
            apache_beam.ParDo(firestore_database.StoreImageAttributeDoFn(), image_provider,job_name)

        if known_args.output:
            filtered_elements | 'Write' >> WriteToText(known_args.output)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
