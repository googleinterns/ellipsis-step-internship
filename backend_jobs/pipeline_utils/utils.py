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
    return str(datetime.timestamp(datetime.now())).replace('.','')

def generate_job_name(pipeline_type, provider):
    """ Returns a unique job_name given pipeline_type and a provider.

    Args:
      pipeline_type: Type str e.g. 'ingestion' or 'recognition'.
      provider: Type ImageProvider/ ImageRecognitionProvider.

    Returns:
      A unique job_name type str.
    """
    job_name = '{pipeline_type}_{provider}_{time_id}'.format(
      pipeline_type = pipeline_type,
      time_id = get_timestamp_id(),
      provider = provider.provider_id.lower())
      # Dataflow job names can only include '-' and not '_'.
    return job_name.replace('_','-')
