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

from abc import ABC, abstractmethod
import apache_beam
from backend_jobs.pipeline_utils import database_schema
from backend_jobs.pipeline_utils.firestore_database import initialize_db


class IngestionRemovalPipelineInterface(ABC, apache_beam.DoFn):
    """ This interface contains functions for all of the removal pipeline stages.
    """

    db = initialize_db()
    
    @abstractmethod
    def get_batched_dataset_and_delete_from_database(self, num_of_batch, remove_by_arg):
        """ Queries firestore database for pipeline runs ingested by the given
        image provider or pipeline run, and deletes the documents from the database .

        Args:
            num_of_batch: The lower limit for querying the database by the random field.
            remove_by_arg: Either the pipeline run id or the image provider id.

        Yields:
            A tuple containing a parent image id and the image provider/pipeline run id.
        """

    @abstractmethod
    def update_arrays_in_image_docs(self, element, remove_by_arg):
        """ This function queries if exists any other pipeline_run/provider in the subcollection
        and updates the ingested providers array / ingested pipeline runs array accordingly.

        Args:
            element: A tuple with two arguments, the first is the parent image id and the second can be
            a list of providers/ pipeline runs e.g. ['parent_id',['run1','run2']]
            remove_by_arg: Either the pipeline run id or the image provider id.


        Returns:
            parent_image_id: The id of the image doc in the image collection.
        """

    def update_provider_and_pipeline_arrays(
            self, query_provider, query_pipeline_run, parent_image_ref,
            image_provider=None, pipeline_run=None):
        """ This function calculates whether we need to update the ingested providers array,
        the ingested runs array, neither or both.

        Args:
            query_provider: All docs with the image_provider as provider.
            query_pipeline_run: All docs with the pipeline_run as pipeline_run.
            parent_image_ref: A reference to the image doc in the image collection.
            image_provider: The image provider we remove the images by.
            pipeline_run: The image pipeline_run we remove the images by.
        """
        if len(query_provider.get()) == 0 and len(query_pipeline_run.get()) != 0:
            self._update_provider_array(parent_image_ref, image_provider)
        if len(query_provider.get()) != 0 and len(query_pipeline_run.get()) == 0:
            self._update_pipeline_array(parent_image_ref, pipeline_run)
        if len(query_provider.get()) == 0 and len(query_pipeline_run.get()) == 0:
            self._update_provider_array(parent_image_ref, image_provider)
            self._update_pipeline_array(parent_image_ref, pipeline_run)

    def _update_provider_array(self, parent_image_ref, image_provider):
        """ This function is in charge of removing the given image_provider from the ingested providers
        array.

        Args:
            parent_image_ref: A reference to the image doc in the image collection.
            image_provider: The image provider we remove the images by.
        """
        image_doc_dict = parent_image_ref.get().to_dict()
        # Updates the provider array in the image collection.
        providers_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS]
        if image_provider in providers_array:
            providers_array.remove(image_provider)
        parent_image_ref.update({
            database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS: providers_array
        })

    def _update_pipeline_array(self, parent_image_ref, pipeline_run):
        """ This function is in charge of removing the given pipeline_run from the ingested pipeline runs
        array.

        Args:
            parent_image_ref: A reference to the image doc in the image collection.
            pipeline_run: The image pipeline_run we remove the images by.
        """
        image_doc_dict = parent_image_ref.get().to_dict()
        # Updates the pipeline array in the image collection.
        pipeline_runs_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS]
        if pipeline_run in pipeline_runs_array:
            pipeline_runs_array.remove(pipeline_run)
        parent_image_ref.update({
            database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS: pipeline_runs_array
        })

    def remove_image_doc_if_necessary(self, parent_image_id):
        ''' This function is in charge of removing the original image if the subcollection
        pipeline_runs does not contain any documents
        (both the arrays ingested pipeline runs and ingested providers are empty).

        Args:
            parent_image_id: The id of the image doc in the image collection.
        '''
        parent_image_ref = self.db.collection(database_schema.COLLECTION_IMAGES).document(parent_image_id)
        image_doc_dict = parent_image_ref.get().to_dict()
        providers_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS]
        pipeline_runs_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_INGESTED_RUNS]
        # If there are no images in the subcollection remove the image.
        if len(pipeline_runs_array) == 0 and len(providers_array) == 0:
            parent_image_ref.delete()  # Delete label doc from database.
