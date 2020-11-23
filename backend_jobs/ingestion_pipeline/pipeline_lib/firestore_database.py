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


class StoreImageAttributeDoFn(apache_beam.DoFn):
    """ Stores asynchronously the entity of ImageAttributes type from each image in the
    projects database.
    """
    def setup(self):
        self.database_firebase = firestore_database.initialize_db()

    def process(self, element, provider, job_name):
        """ Adds/Updates the projects database to contain documents with image attributes.
        In addition it adds for each image a sub collection with information
        on the pipelinerun and the provider.

        Args:
            element: ImageAttribute field
            provider: the provider we are running now
            job_name: the job name that we are running now
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
        _upload_sub_collection(element, provider, job_name, sub_collection_doc_ref)

def _add_document(element, provider, job_name, doc_ref):
    geo_point_coordinates = firestore.GeoPoint(
        float(element.coordinates['latitude']),
        float(element.coordinates['longitude']))
    doc_ref.set({
        database_schema.URL: element.url,
        database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS: [provider.provider_name],
        database_schema.INGESTED_RUNS: [job_name],
        database_schema.COORDINATES: geo_point_coordinates,
        database_schema.DATE_INGESTED: datetime.now(),
        database_schema.DATE_SHOT: element.date_shot,
        database_schema.DATE_FIELDS:_get_date_fields(element.date_shot),
        database_schema.HASHMAP: _get_geo_hashes_map(element.coordinates),
        database_schema.IMAGE_ATTRIBUTES:{
            database_schema.FORMAT: element.format,
            database_schema.RESOLUTION:element.resolution},
        database_schema.ATTRIBUTION: element.attribution,
        database_schema.RANDOM: random.random(),
        database_schema.VISIBILITY: provider.visibility,
    })

def _update_document(provider,doc, doc_ref,job_name):
    ingested_runs = doc.to_dict()[database_schema.INGESTED_RUNS]
    ingested_runs.append(job_name)
    ingested_providers = doc.to_dict()[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS]
    if provider.provider_name not in ingested_providers:
        ingested_providers.append(provider.provider_name)
    doc_ref.update({
        database_schema.INGESTED_RUNS: ingested_runs,
        database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS: ingested_providers,
        database_schema.VISIBILITY: _get_max_visibility(
            provider.visibility,
            doc.to_dict()[database_schema.VISIBILITY]),
    })

def _upload_sub_collection(element, provider,job_name, sub_collection_doc_ref):
    sub_collection_doc_ref.set({
        database_schema.PROVIDER_ID:provider.provider_id,
        database_schema.PROVIDER_NAME:provider.provider_name,
        database_schema.PROVIDER_VERSION: provider.provider_version,
        database_schema.PROVIDER_VISIBILITY: provider.visibility,
        database_schema.PIPELINE_RUN_ID: job_name,
        database_schema.HASHMAP: _get_geo_hashes_map(element.coordinates),
    })

def _get_geo_hashes_map(coordinates):
    """ This function, given a coordinates (lat,long), calculates the geohash
    and builds a map containing a geohash in different lengths.

    Args:
        coordinates: Coordinates in the format {'latitude':float,'longitude':float}.

    Returns:
        A dict contaning geohash in all the diffrent lengths
        e.g.: {'hash1':'d', 'hash2':'dp', 'hash3':'dph', ... 'hash10':'dph1qz7y88',}.
    """
    geo_hashes_map={}
    geohash=geohash2.encode(coordinates['latitude'],coordinates['longitude'])
    for i in range(1,11,1):
        geo_hashes_map['hash'+str(i)]= geohash[0:i]
    return geo_hashes_map

def _get_date_fields(date):
    """ This function converts a datetime object to a map object contaning the date.

    Args:
        date: Type datetime.

    Returns:
        map object in the format {'year':int, 'month':int, 'day':int}.
    """
    year = date.year
    month = date.month
    day = date.day
    date_fields = {'year': year, 'month': month, 'day': day}
    return date_fields

def _get_max_visibility(first_visibility,second_visibility):
    """ This function returns the max visibility between two given visibilities.

    Args:
        first_visibility: VISIBLE or INVISIBLE.
        second_visibility: VISIBLE or INVISIBLE.

    Returns:
        max visibility.
    """
    if first_visibility== database_schema.LABEL_VISIBILITY_VISIBLE  or second_visibility == database_schema.LABEL_VISIBILITY_VISIBLE :
        return database_schema.LABEL_VISIBILITY_VISIBLE 
    return database_schema.LABEL_VISIBILITY_INVISIBLE 
