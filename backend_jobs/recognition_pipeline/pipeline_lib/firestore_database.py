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

RANGE_OF_BATCH = 10
# Defines the range of the random field to query the databse by batches, \
# each batch covers all documents with random value of X up to value of X+RANGE_OF_BATCH
COLLECTION_NAME = 'test'

def initialize_db():
    """Initializes project's Firestore database for writing and reading purposes.

    """
    # pylint: disable=protected-access
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        'projectId': 'step-project-ellispis',
        })
    return firestore.client()

# pylint: disable=abstract-method
class GetBatchedDataset(beam.DoFn):
    """Queries the project's database to get the image dataset to label.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element, ingestion_provider = None, ingestion_run = None):
        """Queries firestore database for images from
        the ingestion_provider within a random range (by batch).

        Args:
            element: the lower limit for querying the database by the random field.
            ingestion_provider: the input of the pipeline, determines the images dataset.
            ingestion_run: the input of the pipeline, determines the dataset.

        Returns:
            A list of dictionaries with all the information (fields and id)
            of each one of the Firestore query's image documents.
        """
        random_min = element
        random_max = element+RANGE_OF_BATCH-1
        # the higher limit for querying the database by the random field.
        if ingestion_run:
            query = self.db.collection(COLLECTION_NAME).\
                where(u'ingestedRuns',u'array_contains', ingestion_run).\
                    where(u'random', u'>=', random_min).where(u'random', u'<=', random_max).stream()
        else:
            query = self.db.collection(COLLECTION_NAME).\
                where(u'ingestedProviders', u'array_contains', ingestion_provider).\
                    where(u'random', u'>=', random_min).where(u'random', u'<=', random_max).stream()
        return [add_id_to_dict(doc) for doc in query]

def add_id_to_dict(doc):
    """ Adds the document's id to the document's fields dictionary.

    """
    full_dict = doc.to_dict()
    full_dict['id'] = doc.id
    return full_dict

class UploadToDatabase(beam.DoFn):
    """Uploads parallelly the label information to the project's database.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element, run_id):
        """Updates the project's database to contain documents with the currect fields
        for each label in the Labels subcollection of each image.

        Args:
            element: tuple of image document dict and a list of all label Ids.
        """
        doc_id = element[0]['id']
        subcollection_ref = self.db.collection(COLLECTION_NAME).document(doc_id).\
            collection(u'Labels')
        for label in element[1]:
            doc = subcollection_ref.document()
            doc.set({
                u'providerId': 'google_vision_api',
                u'providerVersion': '2.0.0',
                u'labelName': label['name'],
                u'visibility': 0,
                u'parentImageId': doc_id,
                u'pipelineRunId': run_id,
                u'hashmap': element[0]['geoHashes'],
                u'random': element[0]['random']
            })
            if 'id' in label:
                doc.set({
                    u'labelId': label['id']
                }, merge = True)

def upload_to_pipeline_runs_collection(provider_id, run_id):
    """ Uploads inforamtion about the pipeline run to the Firestore collection

    """
    # pylint: disable=fixme
    # TODO: get start, end and quality of current pipeline run.
    db = initialize_db()
    db.collection(u'RecognitionPipelineRuns').document().set({
        u'providerId': provider_id,
        u'startDate': 00,
        u'endDate': 00,
        u'quality': 00,
        u'visibility': 0,
        u'pipelineRunId': run_id
    })
