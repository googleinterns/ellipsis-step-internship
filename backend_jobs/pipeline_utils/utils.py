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
from datetime import datetime
from backend_jobs.pipeline_utils.firestore_database import RANGE_OF_BATCH


def get_timestamp_id():
    """ Returns a string with only numbers as time id.
    The string will be used as a unique id for each dataflow job.

    """
    return str(datetime.timestamp(datetime.now())).replace('.', '')


def generate_cloud_dataflow_job_name(pipeline_type, additional_info):
    """ Returns a unique job_name given pipeline_type and a provider.
    Strips '_' and changes it to '-' since Dataflow does not support it.

    Args:
      pipeline_type: Type str e.g. 'ingestion' or 'recognition'.
      additional info: can be an ingestion provider id/ recognition provider id/
      pipeline run id, etc.

    Returns:
      A unique job_name type str.
    """
    job_name = '{pipeline_type}_{additional_info}_{time_id}'.format(
      pipeline_type=pipeline_type,
      time_id=get_timestamp_id(),
      additional_info=str(additional_info).lower())
      # Dataflow job names can only include '-' and not '_'.
    return job_name.replace('_', '-')


def validate_one_arg(image_provider=None, pipeline_run=None):
    """ Checks whether we only get one arguments.
    If not - throws an error.

    Args:
        image_provider: The image provider from whom we are removing the images.
        pipeline_run: The image pipeline_run from whom we are removing the images.

    Raises:
        Raises an error if both image_provider and pipeline_run
        are provided, or nether ar provided.
    """
    if pipeline_run is not None and image_provider is not None:
        raise ValueError('can only get image_provider or pipeline_run')
    if pipeline_run is None and image_provider is None:
        raise ValueError('missing input e.g. image_provider or pipeline_run')


def create_query_indices():
    """ Creates a list of indices for querying the database.

    """
    return [i for i in range(int(1/RANGE_OF_BATCH))]
