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


def get_timestamp_id():
    """ Returns a string with only numbers as time id.
    The string will be used as a unique id for each dataflow job.

    """
    return str(datetime.timestamp(datetime.now())).replace('.', '')


def generate_cloud_dataflow_job_name(pipeline_type, provider):
    """ Returns a unique job_name given pipeline_type and a provider.
    Strips '_' and changes it to '-' since Dataflow does not support it.

    Args:
      pipeline_type: Type str e.g. 'ingestion' or 'recognition'.
      additional info: can be an ingestion provider id/ recognition provider id/
      pipeline run id, etc.

    Returns:
      A unique job_name type str.
    """
    job_name = '{pipeline_type}_{provider}_{time_id}'.format(
      pipeline_type=pipeline_type,
      time_id=get_timestamp_id(),
      provider=provider.provider_id.lower())
    return job_name.replace('_', '-')
