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
import geohash2
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
      pipeline_type = pipeline_type,
      time_id = get_timestamp_id(),
      additional_info = additional_info.lower())
      # Dataflow job names can only include '-' and not '_'.
    return job_name.replace('_','-')

def create_query_indices():
    """ Creates a list of indices for querying the database.

    """
    return [i for i in range(int(1/RANGE_OF_BATCH))]

def get_geo_hashes_map(latitude, longitude):
    """ This function, given a coordinates (lat,long), calculates the geohash
    and builds a map containing a geohash in different lengths.

    Args:
        coordinates: Coordinates in the format {'latitude': float, 'longitude': float}.

    Returns:
        A dict contaning geohash in all the diffrent lengths
        e.g.: {'hash1':'d', 'hash2':'dp', 'hash3':'dph', ... 'hash10':'dph1qz7y88',}.
    """
    geo_hashes_map = {}
    geohash = geohash2.encode(latitude, longitude)
    for i in range(1, 11):
        geo_hashes_map['hash' + str(i)] = geohash[0:i]
    return geo_hashes_map