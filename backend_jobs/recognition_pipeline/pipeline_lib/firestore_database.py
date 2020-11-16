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
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import apache_beam as beam
from pipeline_lib.constants import *

RANGE_OF_BATCH = 0.1
# Defines the range of the random field to query the database by batches, \
# each batch covers all documents with random value of X up to value of X+RANGE_OF_BATCH
INVISIBLE = 0

def initialize_db():
    """Initializes project's Firestore database for writing and reading purposes.

    """
    # pylint: disable=protected-access
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        PROJECT_ID: 'step-project-ellispis',
        })
    return firestore.client()

# pylint: disable=abstract-method
class GetBatchedImageDataset(beam.DoFn):
    """Gets the images data set by batches as requested by
    the pipeline's input from the project's Firestore database.

    Input:
       integer index between 0 and 9.

    Output:
        generator of image's documents in a dictionary form.
        Each image is represented by a dict containing all the fields
        in the database and their values.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element, ingestion_provider = None, ingestion_run = None):
        """Queries firestore database for images from
        the ingestion_provider within a random range (by batch).

        Args:
            element: the index used for querying the database by the random field.
            ingestion_provider: the input of the pipeline, determines the images dataset.
            ingestion_run: the input of the pipeline, determines the dataset.

        Returns:
            A generator of dictionaries with all the information (fields and id)
            of each one of the Firestore data set's image documents.
        """
        random_min = element*RANGE_OF_BATCH
        # the lower limit for querying the database by the random field.
        random_max = random_min+RANGE_OF_BATCH
        # the higher limit for querying the database by the random field.
        if ingestion_run:
            query = self.db.collection(IMAGES_COLLECTION_NAME).\
                where(INGESTED_RUNS,u'array_contains', ingestion_run).\
                    where(RANDOM, u'>=', random_min).where(RANDOM, u'<', random_max).stream()
        else:
            query = self.db.collection(IMAGES_COLLECTION_NAME).\
                where(INGESTED_PROVIDERS, u'array_contains', ingestion_provider).\
                    where(RANDOM, u'>=', random_min).where(RANDOM, u'<', random_max).stream()
        return (add_id_to_dict(doc) for doc in query)

def add_id_to_dict(doc):
    """ Adds the document's id to the document's fields dictionary.

    """
    full_dict = doc.to_dict()
    full_dict['id'] = doc.id
    return full_dict

# pylint: disable=missing-function-docstring
def get_redefine_map(recognition_provider_id):
    db = initialize_db()
    doc_dict = db.collection(REDEFINE_MAPS_COLLECTION_NAME).document(recognition_provider_id).get().to_dict()
    return doc_dict[REDEFINE_MAP]

class StoreInDatabase(beam.DoFn):
    """Stores parallelly the label information in the project's database.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element, run_id, provider_id):
        """Updates the project's database to contain documents with the currect fields
        for each label in the Labels subcollection of each image.

        Args:
            element: tuple of image document dict and a list of all label names and Ids.
        """
        image_doc = element[0]
        doc_id = image_doc['id']
        subcollection_ref = self.db.collection(IMAGES_COLLECTION_NAME).document(doc_id).\
            collection(LABELS_COLLECTION_NAME)
        for label in element[1]:
            doc = subcollection_ref.document()
            doc.set({
                PROVIDER_ID: provider_id,
                PROVIDER_VERSION: '2.0.0',
                LABEL_NAME: label['name'],
                VISIBILITY: INVISIBLE,
                PARENT_IMAGE_ID: doc_id,
                PIPELINE_RUN_ID: run_id,
                HASHMAP: image_doc['geoHashes'],
                RANDOM: image_doc['random']
            })
            if 'id' in label:
                doc.set({
                    LABEL_ID: label['id']
                }, merge = True)

def upload_to_pipeline_runs_collection(provider_id, run_id):
    """ Uploads information about the pipeline run to the Firestore collection

    """
    # pylint: disable=fixme
    # TODO: get start, end and quality of current pipeline run.
    db = initialize_db()
    db.collection(PIPELINE_RUNS_COLLECTION_NAME).document().set({
        PROVIDER_ID: provider_id,
        START_DATE: 00,
        END_DATE: 00,
        VISIBILITY: INVISIBLE,
        PIPELINE_RUN_ID: run_id
    })
