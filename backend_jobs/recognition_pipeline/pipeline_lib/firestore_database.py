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
from backend_jobs.pipeline_utils import database_schema
from backend_jobs.pipeline_utils.firestore_database import initialize_db

# Defines the range of the random field to query the database by batches.
_RANGE_OF_BATCH = 0.1

# pylint: disable=abstract-method
class GetBatchedImageDataset(beam.DoFn):
    """Gets the images data set by batches as requested by
    the pipeline's input from the project's Firestore database.

    Input:
       integer index between 0 and 9.

    Output:
        generator of image's documents in a Python dictionary form.
        Each image is represented by a dict containing all the fields
        of the document in the database and their values.

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
            Only one out of ingestion_provider and ingestion_run is provided.

        Returns:
            A generator of dictionaries with all the information (fields and id)
            of each one of the Firestore data set's image documents.

        Raises:
            Value error if both ingestion_provider and ingestion_run
            are provided.

        """
        if ingestion_provider and ingestion_run:
            raise ValueError('both ingestion provider and run are provided - there should be only one')
        # The lower limit for querying the database by the random field.
        random_min = element * _RANGE_OF_BATCH
        # The higher limit for querying the database by the random field.
        random_max = random_min + _RANGE_OF_BATCH
        if ingestion_run:
            query = self.db.collection(database_schema.COLLECTION_IMAGES).\
                where(database_schema.INGESTED_RUNS,u'array_contains', ingestion_run).\
                    where(database_schema.RANDOM, u'>=', random_min).\
                        where(database_schema.RANDOM, u'<', random_max).stream()
        else:
            query = self.db.collection(database_schema.COLLECTION_IMAGES).\
                where(database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS, u'array_contains', ingestion_provider).\
                    where(database_schema.RANDOM, u'>=', random_min).\
                        where(database_schema.RANDOM, u'<', random_max).stream()
        return (add_id_to_dict(doc) for doc in query)

def add_id_to_dict(doc):
    """ Adds the document's id to the document's fields dictionary.

    """
    full_dict = doc.to_dict()
    full_dict['id'] = doc.id
    return full_dict

class UpdateImageLabelsInDatabase(beam.DoFn):
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
            element: tuple of image document dictionary (Each image is represented by a
            Python dictionary containing all the fields of the document in the database
            and their values) and a list of all labels.

        """
        image_doc = element[0]
        doc_id = image_doc['id']
        subcollection_ref = self.db.collection(database_schema.COLLECTION_IMAGES).document(doc_id).\
            collection(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS)
        labels = element[1]
        for label in labels:
            doc = subcollection_ref.document()
            doc.set({
                database_schema.PROVIDER_ID: provider_id,
                database_schema.PROVIDER_VERSION: '2.0.0',
                database_schema.LABEL_NAME: label,
                database_schema.VISIBILITY: database_schema.LABEL_VISIBILITY_INVISIBLE ,
                database_schema.PARENT_IMAGE_ID: doc_id,
                database_schema.PIPELINE_RUN_ID: run_id,
                database_schema.HASHMAP: image_doc[database_schema.HASHMAP],# Redundant for query optimisation reasons.
                database_schema.RANDOM: image_doc[database_schema.RANDOM] # Redundant for query optimisation reasons.
            })
