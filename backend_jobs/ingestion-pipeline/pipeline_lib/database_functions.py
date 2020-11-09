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
import geohash2

IMAGES_COLLECTION=u'imagesIngested25'
IMAGES_SUB_COLLECTION=u'pipelineRun'

def initialize_database():
    """
    Initializes the project's database for writing/reading/updating/deleting purposes.
    """
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        'projectId': 'step-project-ellispis',
        })
    return firestore.client()

class UploadToDatabase(beam.DoFn):
    """
    Uploads in asynchronously the information that was extracted from each
    image to the project's database.
    """
    def setup(self):
        self.database_firebase = initialize_database()

    def get_ref_collection(self):
        return self.database_firebase.collection(IMAGES_COLLECTION)

    def get_doc(self, image_id):
        doc_ref = self.database_firebase.collection(IMAGES_COLLECTION).document(image_id)
        doc = doc_ref.get()
        return doc

    def process(self, element,provider,job_name):
        """
        Adds/Updates the project's database to contain documents with image attributes.
        In addition it adds for each image a sub collection with information
        on the pipelinerun and the provider.
        Args:
            element: ImageAttribute field
        """
        #TODO: add visibility and logic
        doc_ref = self.database_firebase.collection(IMAGES_COLLECTION).document(element.id)
        doc = doc_ref.get()
        sub_doc_ref= doc_ref.collection(IMAGES_SUB_COLLECTION).document()
        if doc.exists:
            #doc found- image has bean ingested already
            ingested_runs = doc.to_dict()[u'ingestedRuns']
            ingested_runs.append(job_name)
            ingested_providers = doc.to_dict()[u'ingestedProviders']
            if provider.provider_id not in ingested_providers:
                ingested_providers.append(provider.provider_id)
            doc_ref.update({
               u'ingestedRuns':ingested_runs,
               u'ingestedProviders': ingested_providers
            })
        else:
            #doc not found- image has not bean ingested already
            geo_point_location=firestore.GeoPoint(
                float(element.location[0]),
                float(element.location[1]))
            doc_ref.set({
                u'url': element.url,
                u'ingestedProviders':[provider.provider_id],
                u'ingestedRuns':[1],
                u'coordinates': geo_point_location,
                u'dateIngested': datetime.now(),
                u'dateShot': element.date_shot,
                u'dateFields':get_date_fields(element.date_shot),
                u'geoHashes': get_geo_hashes_map(element.location),
                u'imageAttributes':{
                    u'format': element.format,
                    u'resolution':element.resolution},
                u'attribution': element.attribution,
                u'random': random.randint(1,101)
            })
        #Adding a doc to the sub collection (pipelinerun) in an image collection
        sub_doc_ref.set({
            u'coordinates': element.location,
            u'provider_ID':provider.provider_id,
            u'provider_version': provider.provider_version,
            u'provider_type':element.provider_type.value,
            u'provider_visibility': provider.visibility.value,
            u'pipeline_run': job_name
        })


def get_geo_hashes_map(location):
    """
    This function, given a location (lat,long), calculates the geohash
    and builds a map containing a geohash in different lengths.
    """
    geo_hashes_map={}
    geohash=geohash2.encode(location[0],location[1])
    for i in range(1,10,1):
        geo_hashes_map['hash'+str(i)]= geohash[0:i]
    return geo_hashes_map

def get_date_fields(date):
    """
    This function converts a datetime object to a map object contaning the date
    """
    year=date.year
    month=date.month
    day=date.day
    date_fields={'year':year,'month':month,'day':day}
    return date_fields
