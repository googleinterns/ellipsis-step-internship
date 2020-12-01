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

An Image Recognition pipeline to label images from specific dataset by a specific provider.

The pipeline uses Python's Apache beam library to parallelize the different stages.
The images are taken from a Firestore database and are labeled by a ML provider.
The labeling content is updated in the database for each image.
By the end of the process, the project's admin group get notified.
"""
import apache_beam as beam

from backend_jobs.pipeline_utils.firestore_database import initialize_db
from backend_jobs.pipeline_utils import database_schema

RANGE_OF_BATCH = 0.1


# pylint: disable=abstract-method
class GetBatchedDatasetAndDeleteFromDatabase(beam.DoFn):
    """Queries the project's database to get the labels dataset to remove,
    and deleted the documents from the 'Labels' subcollection in the database.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element, image_provider=None, pipeline_run=None):
        """Queries firestore database for labels recognized by the given
        recognition provider or run and deletes the documents from the
        database (by batch).

        Args:
            element: the lower limit for querying the database by the random field.
            recognition_provider: the input of the pipeline, determines the labels dataset.
            recognition_run: the input of the pipeline, determines the labels dataset.

        Returns:
            A list of dictionaries with all the information (fields and id)
            of each one of the Firestore query's label documents.

         Raises:
            Value error if both recognition_provider and recognition_run
            are provided.

        """
        # The lower limit for querying the database by the random field.
        random_min = element * RANGE_OF_BATCH
        # The higher limit for querying the database by the random field.
        random_max = random_min + RANGE_OF_BATCH
        if image_provider:
            query = self.db\
                .collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
                .where(u'providerId', u'==', image_provider)\
                .where(u'random', u'>=', random_min)\
                .where(u'random', u'<', random_max)\
                .stream()
        else:
            query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
                .where(u'pipelineRunId', u'==', pipeline_run)\
                .where(u'random', u'>=', random_min)\
                .where(u'random', u'<', random_max)\
                .stream()
        for doc in query:
            doc_dict = doc.to_dict()
            yield doc_dict[database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID]
            doc.reference.delete()  # Delete label doc from database.


# pylint: disable=abstract-method
class UpdateArraysInImageDocs(beam.DoFn):
    """Queries the project's database to get the image dataset to label.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element, image_provider=None, pipeline_run=None):
        """

        """
        parent_image_id = element
        parent_image_ref = \
            self.db.collection(database_schema.COLLECTION_IMAGES).document(parent_image_id)

        query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
            .where(
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID,
                u'==',
                parent_image_id)
        if(image_provider):
            query = query\
                .where(
                    database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID,
                    u'==',
                    image_provider)
            if len(query.get()) == 0:
                self._delete_element_from_array(parent_image_ref, image_provider)
        else:
            query = query\
                .where(
                    database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID,
                    u'==',
                    pipeline_run)
            if len(query.get()) == 0:
                self._delete_element_from_array(parent_image_ref, pipeline_run)

    def _delete_element_from_array(self, image_doc_ref, image_provider=None, pipeline_run=None):
        image_doc_dict = image_doc_ref.get().to_dict()
        if image_provider:
            providers_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS]
            if image_provider in providers_array:
                providers_array.remove(image_provider)
            image_doc_ref.update({
                database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS: providers_array
            })
        else:
            pipeline_runs_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS]
            if pipeline_run in pipeline_runs_array:
                pipeline_runs_array.remove(pipeline_run)
            image_doc_ref.update({
                database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS: pipeline_runs_array
            })
    