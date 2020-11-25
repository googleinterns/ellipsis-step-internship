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
from backend_jobs.recognition_pipeline.pipeline_lib.firestore_database import add_id_to_dict

RANGE_OF_BATCH = 0.1

# pylint: disable=abstract-method
class GetBatchedLabelsDataset(beam.DoFn):
    """Queries the project's database to get the image dataset to label.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element, recognition_run):
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
        # the lower limit for querying the database by the random field.
        random_min = element * RANGE_OF_BATCH
        # the higher limit for querying the database by the random field.
        random_max = random_min + RANGE_OF_BATCH
        query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS)\
            .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PIPELINE_RUN_ID, u'==', recognition_run).\
                    where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_RANDOM, u'>=', random_min).\
                        where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_RANDOM, u'<', random_max).stream()
        return (add_id_to_dict(doc) for doc in query)

# pylint: disable=abstract-method
class UpdateDatabase(beam.DoFn):
    """ Updates Firestore Database according to verified labels.

        Changes visibility inside label document in 'Labels' subcollection
        and adds the label id to the 'labels' field in the image document if necessary.
    """

    def setup(self):
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element):
        image_doc_dict = element[0]
        image_label_ids = element[1]
        parent_image_ref = self.db.collection(database_schema.COLLECTION_IMAGES).\
            document(image_doc_dict[database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PARENT_IMAGE_ID])
        self._update_label_doc(parent_image_ref, image_doc_dict['id'], image_label_ids)
        self._update_parent_image_labels_array(parent_image_ref, image_label_ids)

    def _update_label_doc(self, parent_image_ref, doc_id, label_id_list):
        """ Updates the label doc in the database.
        Changes the visibility field inside the label doc to 1 and adds all
        the labels ids recognized in it to a new label ids field.

            Args:
                parent_image_ref: refrence to the parent image document in the database
                doc_id: the label document's id which needs to be updated in the database
                label_id_list: list of label ids that the label was redefined to
        """

        doc_ref = parent_image_ref.collection(\
            database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS).document(doc_id)
        doc_ref.update({
            database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_VISIBILITY: database_schema.LABEL_VISIBILITY_VISIBLE
        })
        doc_ref.set({
            database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_IDS: label_id_list
        }, merge = True)

    def _update_parent_image_labels_array(self, image_doc_ref, label_ids):
        """ Adds the label id to the image's document if it is not already there.

            Args:
                parent_image_ref: refrence to the parent image document in the database
                label_id: the label id which needs to be added to the labels array
                of the parent image document in the database

        """
        image_doc_dict = image_doc_ref.get().to_dict()
        labels_array = []
        if database_schema.COLLECTION_IMAGES_FIELD_LABELS in image_doc_dict:
            labels_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_LABELS]
        for label_id in label_ids:
            # label_name = id_to_name(label_id) # TODO: after demo - change to ids not names.
            # if label_name not in labels_array:
            if label_id not in labels_array:
                labels_array.append(label_id) # label name instead for demp
            image_doc_ref.update({
                database_schema.COLLECTION_IMAGES_FIELD_LABELS: labels_array
            })

def id_to_name(label_id): # This method is temp - only for the demo
    labeltag_doc_ref = initialize_db().collection(database_schema.COLLECTION_LABEL_TAGS).\
        document(label_id)
    return labeltag_doc_ref.get().to_dict()['name']

def update_pipelinerun_doc_to_visible(pipeline_run_id):
    """ Updates the pipeline run's document in the Pipeline runs Firestore collection
    to visible after the labels were validated.

    """
    doc_ref = initialize_db().collection(database_schema.COLLECTION_PIPELINE_RUNS).\
        document(pipeline_run_id)
    doc_ref.update({
            u'visibility': database_schema.LABEL_VISIBILITY_VISIBLE
        })

def get_provider_id_from_run_id(run_id):
    """ Returns provider id of the specific run's id.

    """
    run_doc_ref = initialize_db().collection(database_schema.COLLECTION_PIPELINE_RUNS).\
        document(run_id)
    run_doc_dict = run_doc_ref.get().to_dict()
    return run_doc_dict[database_schema.COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID]