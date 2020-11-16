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

import random
from datetime import datetime
import apache_beam as beam
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import firestore as cloud_firestore
import geohash2

_IMAGES_COLLECTION = u'test'
_PIPELINE_COLLECTION = u'IngestionPipelineRun'
_IMAGES_SUB_COLLECTION = u'pipelineRun'

# pylint: disable=protected-access,attribute-defined-outside-init,arguments-differ,abstract-method
def initialize_database():
    """ Initializes the projects database for writing/reading/updating/deleting purposes.

    Returns: 
    """
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        'projectId': 'step-project-ellispis',
        })
    return firestore.client()


class StoreImageAttributeDoFn(beam.DoFn):
    """ Stores asynchronously the entity of ImageAttributes type from each image in the
    projects database.
    """
    def setup(self):
        self.database_firebase = initialize_database()

    def process(self, element, provider, job_name):
        """ Adds/Updates the projects database to contain documents with image attributes.
        In addition it adds for each image a sub collection with information
        on the pipelinerun and the provider.

        Args:
            element: ImageAttribute field
            provider: the provider we are running now
            job_name: the job name that we are running now
        """
        doc_ref = self.database_firebase.collection(_IMAGES_COLLECTION).document(element.image_id)
        doc = doc_ref.get()
        sub_collection_ref = doc_ref.collection(_IMAGES_SUB_COLLECTION)
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
    geo_point_coordinates = cloud_firestore.GeoPoint(
        float(element.coordinates['latitude']),
        float(element.coordinates['longitude']))
    doc_ref.set({
        u'url': element.url,
        u'ingestedProviders': [provider.provider_id],
        u'ingestedRuns': [job_name],
        u'coordinates': geo_point_coordinates,
        u'dateIngested': datetime.now(),
        u'dateShot': element.date_shot,
        u'dateFields':get_date_fields(element.date_shot),
        u'geoHashes': get_geo_hashes_map(element.coordinates),
        u'imageAttributes':{
            u'format': element.format,
            u'resolution':element.resolution},
        u'attribution': element.attribution,
        u'random': random.random(),
        u'visibility': provider.visibility.value,
    })

def _update_document(provider,doc, doc_ref,job_name):
    ingested_runs = doc.to_dict()[u'ingestedRuns']
    ingested_runs.append(job_name)
    ingested_providers = doc.to_dict()[u'ingestedProviders']
    if provider.provider_id not in ingested_providers:
        ingested_providers.append(provider.provider_id)
    doc_ref.update({
        u'ingestedRuns':ingested_runs,
        u'ingestedProviders': ingested_providers,
        u'visibility': max(provider.visibility.value, doc.to_dict()[u'visibility']),
    })

def _upload_sub_collection(element, provider,job_name, sub_collection_doc_ref):
    sub_collection_doc_ref.set({
        u'coordinates': element.coordinates,
        u'providerId':provider.provider_id,
        u'providerVersion': provider.provider_version,
        u'providerVisibility': provider.visibility.value,
        u'pipelineRun': job_name,
        u'geoHashes': get_geo_hashes_map(element.coordinates),
    })


def get_geo_hashes_map(coordinates):
    """ This function, given a coordinates (lat,long), calculates the geohash
    and builds a map containing a geohash in different lengths.

    Returns:
        map object
    """
    geo_hashes_map={}
    geohash=geohash2.encode(coordinates['latitude'],coordinates['longitude'])
    for i in range(1,11,1):
        geo_hashes_map['hash'+str(i)]= geohash[0:i]
    return geo_hashes_map

def get_date_fields(date):
    """ This function converts a datetime object to a map object contaning the date

    Returns:
        map object in the format {'year':int,'month':int,'day':int}
    """
    year = date.year
    month = date.month
    day = date.day
    date_fields = {'year': year, 'month': month, 'day': day}
    return date_fields

def get_doc_by_id(image_id):
    """ This function given a id returns a the doc in IMAGES_COLLECTION

    Returns:
        document
    """
    database_firebase = initialize_database()
    doc_ref = database_firebase.collection(_IMAGES_COLLECTION).document(image_id)
    doc = doc_ref.get()
    return doc