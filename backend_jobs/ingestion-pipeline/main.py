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
from datetime import datetime
import argparse
import logging
import apache_beam as beam
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from providers import image_provider_flickr
from pipeline_lib import database_functions

#Global name for the job that will run
JOB_NAME = 'ingestion' + str(int(datetime.timestamp(datetime.now())))
IMAGE_PROVIDERS = {'FlickrProvider': image_provider_flickr.FlickrProvider}

# pylint: disable=fixme
#TODO: write a filtering function that takes into consideration all attributes
#such as invalid resolution date and more
def filtered_images(element):
    return (element.url is not None and
    element.location is not None and
    element.format is not None and
    element.resolution['width'] >100 and
    element.resolution['height'] > 100)

def get_image_provider(provider_name):
    return IMAGE_PROVIDERS[provider_name]()

def run(argv=None):
    """
    Main entry point; defines and runs the image ingestion pipeline.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_provider_name',
        dest='input_provider_name',
        default='FlickrProvider',
        help='Provider name to process.')
    parser.add_argument(
        '--input_query_tag',
        dest='input_query_tag',
        default='cat',
        help='label ro query by.')
    parser.add_argument(
        '--output',
        dest='output',
        help='Output file to write results to.')
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args,job_name=JOB_NAME)

    # The pipeline will be run on exiting the with block.
    # pylint: disable=expression-not-assigned
    with beam.Pipeline(options=pipeline_options) as pipeline:

        api_provider= get_image_provider(known_args.input_provider_name)
        query_by_arguments_map={'tag':known_args.input_query_tag}
        num_of_batches= api_provider.get_num_of_batches(query_by_arguments_map)
        create_batch = (pipeline | 'create' >> beam.Create(
            [i for i in range(1, int(1)+1, 1)]) )
        images = create_batch | 'call API' >> beam.ParDo(
            api_provider.get_images,
            api_provider.num_of_images,
            query_by_arguments_map)
        extracted_elements = images | 'extract attributes' >> beam.Map(
            api_provider.get_image_attributes)
        filtered_elements = extracted_elements | 'filter' >> beam.Filter(filtered_images)
        filtered_elements | 'upload' >> beam.ParDo(
            database_functions.UploadToDatabase(),api_provider,JOB_NAME)

        if known_args.output:
            filtered_elements | 'Write' >> WriteToText(known_args.output)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
    