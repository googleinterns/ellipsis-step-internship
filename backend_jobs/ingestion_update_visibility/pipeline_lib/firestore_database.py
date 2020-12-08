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

import apache_beam
from backend_jobs.pipeline_utils.firestore_database import initialize_db
from backend_jobs.pipeline_utils.firestore_database import add_id_to_dict
from backend_jobs.pipeline_utils import database_schema
from backend_jobs.pipeline_utils import utils
from backend_jobs.pipeline_utils import constants


class GetDataset(apache_beam.DoFn):
    """Queries the project's database to get the image dataset to update."""
    
    def __init__(self, image_provider=None, pipeline_run=None):
        utils.validate_one_arg(image_provider, pipeline_run)
        self.image_provider = image_provider
        self.pipeline_run = pipeline_run
    
    def setup(self):
        self.db = initialize_db()

    def process(self, element, ):
        """Queries firestore database for images given a image_provider/ pipeline_run
        within a random range (by batch).

        Args:
            element: the lower limit for querying the database by the random field.
            image_provider: the input of the pipeline, determines to update by image provider.
            pipeline_run: the input of the pipeline, determines to update by pipeline run.

        Returns:
            A list of dictionaries with all the information (fields and id)
            of each one of the Firestore query's image documents.
        """
        
        # the lower limit for querying the database by the random field.
        random_min = element * constants.RANGE_OF_BATCH
        # the higher limit for querying the database by the random field.
        random_max = random_min + constants.RANGE_OF_BATCH
        if self.image_provider:
            query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
                .where(
                    database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID,
                    u'==',
                    self.image_provider)\
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'>=', random_min)\
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'<', random_max)\
                .stream()
        else:
            query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
                .where(
                    database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID,
                    u'==',
                    self.pipeline_run)\
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'>=', random_min)\
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'<', random_max)\
                .stream()
        return (add_id_to_dict(doc) for doc in query)


class UpdateVisibilityInDatabase(apache_beam.DoFn):
    """ Updates Firestore Database visibility field to visible.
    Updates visibility inside pipeline document in 'PipelineRuns' subcollection
    and in the 'Images' collection.
    """

    def setup(self):
        self.db = initialize_db()

    def process(self, element, visibility):
        """This function updates the visibility in the Images/ PipelineRun firestore database.

        Args:
            element: A dictionaries with all the information (fields and id) to update.
            visibility: The visibility we are updating the doc to, e.g. 'VISIBLE'/ 'INVISIBLE'
        """
        parent_image_id = element[database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID]
        parent_image_ref = self.db.collection(database_schema.COLLECTION_IMAGES)\
            .document(parent_image_id)
        doc_ref = parent_image_ref.collection(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
            .document(element['id'])
        parent_image_ref.update({
            database_schema.COLLECTION_IMAGES_FIELD_VISIBILITY:
                visibility.value  # TODO: fix functionality to be the max between all doc in subcollection.
        })
        doc_ref.update({
            database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_VISIBILITY:
                visibility.value
        })


def update_pipelinerun_doc_visibility(image_provider_id, visibility):
    """ Updates the pipeline run's document in the Pipeline runs Firestore collection to the
    given visibility.

    Args:
        image_provider_id: The providers id.
        visibility: The visibility we are updating the doc to, e.g. 'VISIBLE'/ 'INVISIBLE'
    """
    doc_ref = initialize_db().collection(database_schema.COLLECTION_PIPELINE_RUNS).\
        document(image_provider_id)
    doc_ref.update({
        database_schema.COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_VISIBILITY: visibility.value
    })
