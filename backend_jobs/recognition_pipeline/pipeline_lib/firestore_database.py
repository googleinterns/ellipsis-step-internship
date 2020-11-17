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
import apache_beam as beam
from backend_jobs.pipeline_utils import constants
from backend_jobs.pipeline_utils.firestore_database import initialize_db

RANGE_OF_BATCH = 0.1
# Defines the range of the random field to query the database by batches, \
# each batch covers all documents with random value of X up to value of X+RANGE_OF_BATCH

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
            query = self.db.collection(constants.IMAGES_COLLECTION_NAME).\
                where(constants.INGESTED_RUNS,u'array_contains', ingestion_run).\
                    where(constants.RANDOM, u'>=', random_min).where(constants.RANDOM, u'<', random_max).stream()
        else:
            query = self.db.collection(constants.IMAGES_COLLECTION_NAME).\
                where(constants.INGESTED_PROVIDERS, u'array_contains', ingestion_provider).\
                    where(constants.RANDOM, u'>=', random_min).where(constants.RANDOM, u'<', random_max).stream()
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
    doc_dict = db.collection(constants.REDEFINE_MAPS_COLLECTION_NAME).document(recognition_provider_id).get().to_dict()
    return doc_dict[constants.REDEFINE_MAP]

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
        subcollection_ref = self.db.collection(constants.IMAGES_COLLECTION_NAME).document(doc_id).\
            collection(constants.LABELS_COLLECTION_NAME)
        for label in element[1]:
            doc = subcollection_ref.document()
            doc.set({
                constants.PROVIDER_ID: provider_id,
                constants.PROVIDER_VERSION: '2.0.0',
                constants.LABEL_NAME: label['name'],
                constants.VISIBILITY: constants.INVISIBLE,
                constants.PARENT_IMAGE_ID: doc_id,
                constants.PIPELINE_RUN_ID: run_id,
                constants.HASHMAP: image_doc['geoHashes'],
                constants.RANDOM: image_doc['random']
            })
            if 'id' in label:
                doc.set({
                    constants.LABEL_ID: label['id']
                }, merge = True)


