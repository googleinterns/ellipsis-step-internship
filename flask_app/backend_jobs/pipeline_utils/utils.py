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
from google.cloud import firestore
from backend_jobs.pipeline_utils import database_schema
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
    for i in range(1, 12):
        geo_hashes_map['hash' + str(i)] = geohash[0:i]
    return geo_hashes_map

def get_quantize_coords_from_geohash(precision, geohash_map):
    """ Returns the quantized coordinates for image's coordinates in the requested precision.

    """
    precision_string = 'hash{precision}'.format(precision=precision)
    lat, lng = geohash2.decode(geohash_map[precision_string])
    return (float(lat), float(lng))

def get_point_key(precision, label_id, hashmap):
    """ Returns a point key that matches the provided arguments.

    """
    return (precision, label_id, get_quantize_coords_from_geohash(\
                        precision, hashmap))

def get_query_from_heatmap_collection(db, label, quantized_coords):
    """ Returns a query from database_schema.COLLECTION_HEATMAP according to the arguments.

    Args:
        label: Label id to query by.
        quantized_coords: the quantized coordinates to query by.

    """
    quantized_coords_lat = quantized_coords[0]
    quantized_coords_lng = quantized_coords[1]
    geopoint_quantized_coords = firestore.GeoPoint(\
        quantized_coords_lat, quantized_coords_lng)
    query = db.collection_group(\
        database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS).\
            where(database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_COORDINATES,\
                u'==', geopoint_quantized_coords).\
                    where(database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_LABEL_ID,\
                        u'==', label).stream()
    return query

def add_point_key_to_heatmap_collection(db, quantized_coords, precision, label, count):
    """ Adds a new point key to database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS.
    The point key will be added to the relevant precision document.

    """
    precision_string_id = 'precision{precision_number}'.format(precision_number=precision)
    quantized_coords_lat = quantized_coords[0]
    quantized_coords_lng = quantized_coords[1]
    geopoint_quantized_coords = firestore.GeoPoint(quantized_coords_lat, quantized_coords_lng)
    db.collection(database_schema.COLLECTION_HEATMAP).document(precision_string_id).\
        collection(database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS).\
            document().set({
                database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_LABEL_ID:\
                    label,
                database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_COORDINATES:\
                    geopoint_quantized_coords,
                database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_WEIGHT:\
                    count,
                database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_HASHMAP:\
                    get_geo_hashes_map(quantized_coords_lat, quantized_coords_lng)
            })
