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
from backend_jobs.pipeline_utils import database_schema
from backend_jobs.pipeline_utils import utils
from backend_jobs.pipeline_utils import constants
from backend_jobs.pipeline_utils import data_types


class GetDataset(apache_beam.DoFn):
    """Queries the project's database to get the image dataset to update."""
    def __init__(self, image_provider=None, pipeline_run=None):
        utils.validate_one_arg(image_provider, pipeline_run)
        self.image_provider = image_provider
        self.pipeline_run = pipeline_run
    
    def setup(self):
        self.db = initialize_db()

    def process(self, element):
        """Queries firestore database for images given an image_provider/ pipeline_run
        within a random range (by batch).

        Args:
            element: the lower limit for querying the database by the random field.

        Yields:
            A tuple containing a parent's image id and the doc id.
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
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'<', random_max) \
                .stream()
        for doc in query:
            doc_dict = doc.to_dict()
            parent_image_id = doc_dict[
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID]
            yield (parent_image_id, doc.id)


class UpdateVisibilityInDatabaseSubcollection(apache_beam.DoFn):
    """ Updates Firestore Database visibility field to the given visibility.
    Updates visibility inside document in the 'PipelineRuns' subcollection.
    """
    def __init__(self, image_provider=None, pipeline_run=None):
        utils.validate_one_arg(image_provider, pipeline_run)
        self.image_provider = image_provider
        self.pipeline_run = pipeline_run

    def setup(self):
        self.db = initialize_db()

    def process(self, element, visibility):
        """This function updates the visibility in PipelineRun subcollection to the given visibility.

        Args:
            element: A tuple containing a parent's image id and the doc id.
            visibility: The visibility we are updating the doc to, e.g. 'VISIBLE'/ 'INVISIBLE'
        """
        parent_image_id = element[0]
        parent_image_ref = self.db.collection(database_schema.COLLECTION_IMAGES)\
            .document(parent_image_id)

        # Only process the image if it passed the ingestion filters.
        if not parent_image_ref.get().to_dict()[database_schema.COLLECTION_IMAGES_FIELD_PASSED_FILTER]:
            return []

        subcollection_ids = element[1]
        for subcollection_id in subcollection_ids:
            doc_ref = parent_image_ref.collection(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
                .document(subcollection_id)
            doc_ref.update({
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_VISIBILITY:
                    visibility.value
            })
        return [parent_image_id]


class UpdateVisibilityInDatabaseCollection(apache_beam.DoFn):
    """ Updates Firestore Database visibility field in the 'Images' collection to the max visibility
    in the subcollection 'PipelineRuns'.
    """
    def __init__(self, image_provider=None, pipeline_run=None):
        utils.validate_one_arg(image_provider, pipeline_run)
        self.image_provider = image_provider
        self.pipeline_run = pipeline_run

    def setup(self):
        self.db = initialize_db()

    def process(self, parent_image_id):
        """This function updates the visibility in the Images collection.

        Args:
            parent_image_id: The image doc id.
        """
        parent_image_ref = self.db.collection(database_schema.COLLECTION_IMAGES)\
            .document(parent_image_id)
        # Only process the image if it passed the ingestion filters.
        if parent_image_ref.get().to_dict()[database_schema.COLLECTION_IMAGES_FIELD_PASSED_FILTER]:
            parent_image_ref.update({
                database_schema.COLLECTION_IMAGES_FIELD_VISIBILITY:
                    self._max_visibility(parent_image_id).value
            })

    def _max_visibility(self, parent_image_id):
        """This function finds the max visibility in the PipelineRun subcollection.

        Args:
            parent_image_id: The image doc id.
        """
        utils.validate_one_arg(self.image_provider, self.pipeline_run)
        query = initialize_db().collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
            .where(
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID,
                u'==',
                parent_image_id)\
            .where(
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_VISIBILITY,
                u'==',
                1)  # 1 == VISIBLE
        if len(query.get()) == 0:
            return data_types.VisibilityType.INVISIBLE
        return data_types.VisibilityType.VISIBLE


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
