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
from backend_jobs.ingestion_removal.pipeline_lib.interface import IngestionRemovalPipelineIntrface
from backend_jobs.pipeline_utils import database_schema
from backend_jobs.pipeline_utils import constants


class IngestionRemovalByProvider(IngestionRemovalPipelineIntrface):
    """ 
    """
    def get_batched_dataset_and_delete_from_database(self, num_of_batch, image_provider):
        # The lower limit for querying the database by the random field.
        random_min = num_of_batch * constants.RANGE_OF_BATCH
        # The higher limit for querying the database by the random field.
        random_max = random_min + constants.RANGE_OF_BATCH
        query = self.db\
            .collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
            .where(
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID, u'==',
                image_provider)\
            .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'>=', random_min)\
            .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'<', random_max)\
            .stream()
        for doc in query:
            doc_dict = doc.to_dict()
            parent_image_id = doc_dict[
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID]
            pipeline_run = doc_dict[
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID]
            yield (parent_image_id, pipeline_run)
            doc.reference.delete()  # Delete label doc from database.

    def update_arrays_in_image_docs(self, element, image_provider):
        parent_image_id = element[0]
        pipeline_runs = element[1]
        parent_image_ref = self.db.collection(database_schema.COLLECTION_IMAGES).document(parent_image_id)
        query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
            .where(
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID,
                u'==',
                parent_image_id)
        query_provider = query\
            .where(
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID,
                u'==',
                image_provider)
        for pipeline_run in pipeline_runs:
            query_pipeline_run = query\
                .where(
                    database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID,
                    u'==',
                    pipeline_run)
            self.delete_if_statements(
                query_provider, query_pipeline_run, parent_image_ref, image_provider, pipeline_run)
