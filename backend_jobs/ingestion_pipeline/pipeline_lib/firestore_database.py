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
import random
import apache_beam
import geohash2
from google.cloud import firestore
from backend_jobs.pipeline_utils import firestore_database
from backend_jobs.pipeline_utils import database_schema
from backend_jobs.ingestion_pipeline.pipeline_lib.data_types import VisibilityType

_RANDOM = random.random()

class AddOrUpdateImageDoFn(apache_beam.DoFn):
    """ Stores asynchronously the entity of ImageAttributes type from each image in the
    projects database.
    """
    def setup(self):
        self.database_firebase = firestore_database.initialize_db()

    def process(self, element, provider, job_name):
        """ Adds/Updates the images collection to contain documents with image attributes.
        In addition it adds for each image a sub collection with information
        on the pipelinerun and the provider.

        Args:
            element: ImageAttribute type.
            provider: Inherits from ImageProvider type.
            job_name: Current job name.
        """
        doc_ref = self.database_firebase \
            .collection(database_schema.COLLECTION_IMAGES) \
            .document(element.image_id)
        doc = doc_ref.get()
        sub_collection_ref = doc_ref.collection(database_schema.COLLECTION_PIPELINE_RUNS)
        sub_collection_doc_ref = sub_collection_ref.document()
        if doc.exists:
            #doc found- image has been ingested already
            _update_document(provider, doc, doc_ref, job_name)
        else:
            #doc not found- image has not been ingested already
            _add_document(element, provider, job_name, doc_ref)
        #Adding a doc to the sub collection (pipelinerun) in the image collection
        _update_sub_collection(element, provider, job_name, sub_collection_doc_ref)

def _add_document(element, provider, job_name, doc_ref):
    geo_point_coordinates = firestore.GeoPoint(element.latitude, element.longitude)
    geo_hashes_map = _get_geo_hashes_map(element.latitude, element.longitude)
    doc_ref.set({
        database_schema.COLLECTION_IMAGES_FIELD_URL: element.url,
        database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS: [provider.provider_name],
        database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS: [job_name],
        database_schema.COLLECTION_IMAGES_FIELD_COORDINATES: geo_point_coordinates,
        database_schema.COLLECTION_IMAGES_FIELD_DATE_INGESTED: datetime.now(),
        database_schema.COLLECTION_IMAGES_FIELD_DATE_SHOT: element.date_shot,
        database_schema.COLLECTION_IMAGES_FIELD_DATE_FIELDS:_get_date_fields(element.date_shot),
        database_schema.COLLECTION_IMAGES_FIELD_HASHMAP: geo_hashes_map,
        database_schema.COLLECTION_IMAGES_FIELD_IMAGE_ATTRIBUTES: {
            database_schema.COLLECTION_IMAGES_FIELD_FORMAT: element.format,
            database_schema.COLLECTION_IMAGES_FIELD_RESOLUTION: {
                database_schema.COLLECTION_IMAGES_FIELD_WIDTH: element.width_pixels,
                database_schema.COLLECTION_IMAGES_FIELD_HEIGHT: element.height_pixels,
            },
        },
        database_schema.COLLECTION_IMAGES_FIELD_ATTRIBUTION: element.attribution,
        database_schema.COLLECTION_IMAGES_FIELD_RANDOM: _RANDOM,
        database_schema.COLLECTION_IMAGES_FIELD_VISIBILITY: provider.visibility.value,
    })

def _update_document(provider, doc, doc_ref, job_name):
    ingested_runs = doc.to_dict()[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS]
    ingested_runs.append(job_name)
    ingested_providers = doc.to_dict()[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS]
    if provider.provider_name not in ingested_providers:
        ingested_providers.append(provider.provider_name)
    doc_ref.update({
        database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS: ingested_runs,
        database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS: ingested_providers,
        database_schema.COLLECTION_IMAGES_FIELD_VISIBILITY: _get_max_visibility(
            VisibilityType(provider.visibility.value),
            doc.to_dict()[database_schema.COLLECTION_IMAGES_FIELD_VISIBILITY]),
    })

def _update_sub_collection(element, provider, job_name, sub_collection_doc_ref):
    geo_hashes_map = _get_geo_hashes_map(element.latitude, element.longitude)
    sub_collection_doc_ref.set({
        database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID: \
            provider.provider_id,
        database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_NAME: \
            provider.provider_name,
        database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_VERSION: \
            provider.provider_version,
        database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_VISIBILITY: \
            provider.visibility.value,
        database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID: \
            job_name,
        database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_HASHMAP: \
            geo_hashes_map,
        database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM: \
            _RANDOM,
        database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID: \
            element.image_id
    })

def _get_geo_hashes_map(latitude, longitude):
    """ This function, given a coordinates (lat,long), calculates the geohash
    and builds a map containing a geohash in different lengths.

    Args:
        coordinates: Coordinates in the format {'latitude':float,'longitude':float}.

    Returns:
        A dict contaning geohash in all the diffrent lengths
        e.g.: {'hash1':'d', 'hash2':'dp', 'hash3':'dph', ... 'hash10':'dph1qz7y88',}.
    """
    geo_hashes_map={}
    geohash=geohash2.encode(latitude, longitude)
    for i in range(1,11):
        geo_hashes_map['hash'+str(i)]= geohash[0:i]
    return geo_hashes_map

def _get_date_fields(date):
    """ This function converts a datetime object to a map object contaning the date.

    Args:
        date: Type datetime.

    Returns:
        map object in the format {'year':int, 'month':int, 'day':int}.
    """
    return {'year': date.year, 'month': date.month, 'day': date.day}

def _get_max_visibility(first_visibility, second_visibility):
    """ This function returns the max visibility between two given visibilities.

    Args:
        first_visibility: VISIBLE or INVISIBLE.
        second_visibility: VISIBLE or INVISIBLE.

    Returns:
        max visibility 0 or 1.
    """
    if first_visibility== VisibilityType.VISIBLE  or second_visibility == VisibilityType.VISIBLE :
        return VisibilityType.VISIBLE.value
    return VisibilityType.INVISIBLE.value

def get_provider_key(provider_id):
    """ This function given a provider id gets the Api key and Secret key
    from the database.

    Args:
        provider_id: string the providers id.

    Returns:
        api_key: string
        secret_key: string
    """
    database = firestore_database.initialize_db()
    doc_dict = database.collection(database_schema.COLLECTION_IMAGE_PROVIDERS).\
        document(provider_id).get().to_dict()
    return doc_dict[database_schema.COLLECTION_IMAGE_PROVIDERS_FIELD_API_KEY],\
        doc_dict[database_schema.COLLECTION_IMAGE_PROVIDERS_FIELD_API_KEY]
