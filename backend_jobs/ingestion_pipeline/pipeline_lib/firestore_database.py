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
from backend_jobs.pipeline_utils import constants


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
        doc_ref = self.database_firebase.collection(constants.IMAGES_COLLECTION_NAME).document(element.image_id)
        doc = doc_ref.get()
        sub_collection_ref = doc_ref.collection(constants.PIPELINE_RUNS_COLLECTION_NAME)
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
        constants.URL: element.url,
        constants.INGESTED_PROVIDERS: [provider.provider_name],
        constants.INGESTED_RUNS: [job_name],
        constants.COORDINATES: geo_point_coordinates,
        constants.DATE_INGESTED: datetime.now(),
        constants.DATE_SHOT: element.date_shot,
        constants.DATE_FIELDS:get_date_fields(element.date_shot),
        constants.HASHMAP: get_geo_hashes_map(element.coordinates),
        constants.IMAGE_ATTRIBUTES:{
            constants.FORMAT: element.format,
            constants.RESOLUTION:element.resolution},
        constants.ATTRIBUTION: element.attribution,
        constants.RANDOM: random.random(),
        constants.VISIBILITY: provider.visibility.value,
    })

def _update_document(provider,doc, doc_ref,job_name):
    ingested_runs = doc.to_dict()[constants.INGESTED_RUNS]
    ingested_runs.append(job_name)
    ingested_providers = doc.to_dict()[constants.INGESTED_PROVIDERS]
    if provider.provider_name not in ingested_providers:
        ingested_providers.append(provider.provider_name)
    doc_ref.update({
        constants.INGESTED_RUNS:ingested_runs,
        constants.INGESTED_PROVIDERS: ingested_providers,
        constants.VISIBILITY: max(provider.visibility.value, doc.to_dict()[constants.VISIBILITY]),
    })

def _upload_sub_collection(element, provider,job_name, sub_collection_doc_ref):
    sub_collection_doc_ref.set({
        constants.PROVIDER_ID:provider.provider_id,
        constants.PROVIDER_NAME:provider.provider_name,
        constants.PROVIDER_VERSION: provider.provider_version,
        constants.PROVIDER_VISIBILITY: provider.visibility.value,
        constants.PIPELINE_RUN_ID: job_name,
        constants.HASHMAP: get_geo_hashes_map(element.coordinates),
    })

def get_geo_hashes_map(coordinates):
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

def get_date_fields(date):
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
