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
from backend_jobs.pipeline_utils import constance


class GetBatchedDatasetAndDeleteFromDatabase(apache_beam.DoFn):
    """Queries the project's database to get the labels dataset to remove,
    and deleted the documents from the 'Labels' subcollection in the database.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element, image_provider=None, pipeline_run=None):
        """Queries firestore database for pipeline runs ingested by the given
        image provider or pipeline run and deletes the documents from the database .

        Args:
            element: the lower limit for querying the database by the random field.
            image_provider: The image provider from whom we are remove the images.
            pipeline_run: The image pipeline_run from whom we are remove the images.

        Yields:
            A tuple containing of a parents image id and the image provider/pipeline run,
            e.g. if in this functions input was an image provider- in the tuple we
            return the pipeline run of the deleted document.
        """
        _valedate_one_arg(image_provider, pipeline_run)
        # The lower limit for querying the database by the random field.
        random_min = element * constance.RANGE_OF_BATCH
        # The higher limit for querying the database by the random field.
        random_max = random_min + constance.RANGE_OF_BATCH
        if image_provider:
            query = self.db\
                .collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID, u'==', image_provider)\
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'>=', random_min)\
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'<', random_max)\
                .stream()
        else:  # if pipeline_run.
            query = self.db\
                .collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID, u'==', pipeline_run)\
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'>=', random_min)\
                .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM, u'<', random_max)\
                .stream()
        for doc in query:
            doc_dict = doc.to_dict()
            parent_image_id = doc_dict[
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID]
            # If we remove by provider we will return the pipeline run to remove if this pipeline run
            # is provider specific.
            if image_provider:
                pipeline_run = doc_dict[
                    database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID]
                yield (parent_image_id, pipeline_run)
            # If we remove by pipeline_run we will return the image provider to remove if the provider
            # is pipeline run specific.
            else:
                image_provider = doc_dict[
                    database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID]
                yield (parent_image_id, image_provider) 
            doc.reference.delete()  # Delete label doc from database.


# pylint: disable=abstract-method
class UpdateArraysInImageDocs(apache_beam.DoFn):
    """Queries the project's database to get the image dataset to label.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    def process(self, element, image_provider=None, pipeline_run=None):
        """ This function queries if exists any other pipeline_run/provider in the subcollection
        and updates the ingested providers array / ingested runs array accordingly.
        This function is incharge of removing the original image if the subcollection pipeline_runs is empty.

        Arguments:
            element: A list with two arguments, the first the parent image id and the second can be
            a list of providers/ pipeline runs e.g. ['parent_id',['run1','run2']]
            image_provider: The image provider from whom we are remove the images.
            pipeline_run: The image pipeline_run from whom we are remove the images.
        """
        _valedate_one_arg(image_provider, pipeline_run)
        parent_image_id = element[0]
        if image_provider:
            pipeline_runs = element[1]
        else:
            image_providers = element[1]
        parent_image_ref = self.db.collection(database_schema.COLLECTION_IMAGES).document(parent_image_id)
        query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS)\
            .where(
                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID,
                u'==',
                parent_image_id)
        if image_provider:
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
                self._delete_if_statements(query_provider, query_pipeline_run, parent_image_ref, image_provider, pipeline_run)
        else:
            query_pipeline_run = query\
                .where(
                    database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID,
                    u'==',
                    pipeline_run)
            for image_provider in image_providers:
                query_provider = query\
                    .where(
                        database_schema.COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID,
                        u'==',
                        image_provider)
                self._delete_if_statements(query_provider, query_pipeline_run, parent_image_ref, image_provider, pipeline_run)

    def _delete_if_statements(
            self, query_provider, query_pipeline_run, parent_image_ref,
            image_provider=None, pipeline_run=None):
        """ This function calculates if whether we need to update the ingested providers array,
        ingested runs array, nether or both.

        Arguments:
            query_provider:
            query_pipeline_run:
            parent_image_ref: A reference to the image doc in the image collection.
            image_provider: The image provider from whom we are removing the images.
            pipeline_run: The image pipeline_run from whom we are removing the images.
        """
        if len(query_provider.get()) == 0 and len(query_pipeline_run.get()) != 0:
            self._updating_array_and_removing_image(parent_image_ref, image_provider=image_provider)
        if len(query_provider.get()) != 0 and len(query_pipeline_run.get()) == 0:
            self._updating_array_and_removing_image(parent_image_ref, pipeline_run=pipeline_run)
        if len(query_provider.get()) == 0 and len(query_pipeline_run.get()) == 0:
            self._updating_array_and_removing_image(parent_image_ref, image_provider=image_provider, pipeline_run=pipeline_run)

    def _updating_array_and_removing_image(self, parent_image_ref, image_provider=None, pipeline_run=None):
        """ This function is incharge of updating the ingested providers and ingested runs arrays,
        if necessary(both arrays are empty) this function removes the image doc itself.

        Arguments:
            parent_image_ref: A reference to the image doc in the image collection.
            image_provider: The image provider from whom we are removing the images.
            pipeline_run: The image pipeline_run from whom we are removing the images.
        """
        image_doc_dict = parent_image_ref.get().to_dict()
        providers_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS]
        pipeline_runs_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS]
        if image_provider:  # Updates the provider array in the image collection.
            providers_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS]
            if image_provider in providers_array:
                providers_array.remove(image_provider)
            parent_image_ref.update({
                database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS: providers_array
            })
        if pipeline_run:  # Updates the pipeline array in the image collection.
            pipeline_runs_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS]
            if pipeline_run in pipeline_runs_array:
                pipeline_runs_array.remove(pipeline_run)
            parent_image_ref.update({
                database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS: pipeline_runs_array
            })
        # If there is no image in the sub collection remove the image.
        if len(pipeline_runs_array) == 0 and len(providers_array) == 0:
            parent_image_ref.delete()  # Delete label doc from database.


def _valedate_one_arg(image_provider=None, pipeline_run=None):
    """ Checks whether we only get one arguments.
    If not - throws an error.

    Arguments:
        image_provider: The image provider from whom we are removing the images.
        pipeline_run: The image pipeline_run from whom we are removing the images.

    Raises:
        Raises an error if both image_provider and pipeline_run
        are provided, or nether ar provided.
    """
    if pipeline_run is not None and image_provider is not None:
        raise ValueError('can only get image_provider or pipeline_run')
    if pipeline_run is None and image_provider is None:
        raise ValueError('missing input e.g. image_provider or pipeline_run')
