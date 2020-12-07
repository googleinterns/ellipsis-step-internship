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

from backend_jobs.pipeline_utils.firestore_database import initialize_db, RANGE_OF_BATCH
from backend_jobs.pipeline_utils import database_schema, data_types
from backend_jobs.recognition_pipeline.pipeline_lib.firestore_database import add_id_to_dict

# pylint: disable=abstract-method
class GetBatchedLabelsDataset(beam.DoFn):
    """Queries the project's database to get the labels needed to be verified.

    Input:
       integer index.

    Output:
        generator of label's documents in a Python dictionary form.
        Each label is represented by a dict containing all the fields
        of the document in the database and their values as stored in
        the database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, index, recognition_run):
        """Queries firestore database for labels recognizied by
        the recognition_run within a random range (by batch).

        Args:
            index: the index for querying the database by the random field.
            recognition_run: the input of the pipeline, determines the labels dataset.

        Returns:
            A generator of dictionaries with all the information (fields and id)
            of each one of the Firestore data set's label documents as stored in
            the database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS.

        """
        # the lower limit for querying the database by the random field.
        random_min = index * RANGE_OF_BATCH
        # the higher limit for querying the database by the random field.
        random_max = random_min + RANGE_OF_BATCH
        query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS)\
            .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PIPELINE_RUN_ID,\
                u'==', recognition_run).where(database_schema.\
                    COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_RANDOM, u'>=', random_min)\
                        .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_RANDOM,\
                            u'<', random_max).stream()
        return (add_id_to_dict(doc) for doc in query)

# pylint: disable=abstract-method
class UpdateDatabaseWithVisibleLabels(beam.DoFn):
    """ Updates Firestore Database according to verified labels.

        Changes visibility inside label document in 'Labels' subcollection
        and adds the label id to the 'labels' field in the image document if necessary.

    Input:
        tuple of a Python Dictionary representing the label document as
        stored in the database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS and
        a list of label ids.
        (label_doc_dict, list_of_label_ids)

    """

    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, label_info):
        """ Updates the Firestore database after verifying the labels.
        Updates parent image doc to include the new label ids.
        Updates the label doc to Visible.

            Args:
                label_info: (label doc Python dictionary, list of label ids)

        """
        image_doc_dict = label_info[0]
        image_label_ids = label_info[1]
        parent_image_ref = self.db.collection(database_schema.COLLECTION_IMAGES).\
            document(image_doc_dict[database_schema.\
                COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PARENT_IMAGE_ID])
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
            database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_VISIBILITY:\
                data_types.VisibilityType.VISIBLE.value
        })
        doc_ref.set({
            database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_IDS: label_id_list
        }, merge = True)

    def _update_parent_image_labels_array(self, image_doc_ref, label_ids):
        """ Adds the label id to the image's document if it is not already there.

            Args:
                image_doc_ref: refrence to the parent image document in the database
                label_id: the label id which needs to be added to the labels array
                of the parent image document in the database

        """
        image_doc_dict = image_doc_ref.get().to_dict()
        labels_array = []
        if database_schema.COLLECTION_IMAGES_FIELD_LABELS in image_doc_dict:
            labels_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_LABELS]
        for label_id in label_ids:
            if label_id not in labels_array:
                labels_array.append(label_id) # label name instead for demo
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
           database_schema.COLLECTION_PIPELINE_RUNS_FIELD_VISIBILITY:\
               data_types.VisibilityType.VISIBLE.value
        })

def get_provider_id_from_run_id(run_id):
    """ Returns the provider id of the specific run's id.

    """
    run_doc_ref = initialize_db().collection(database_schema.COLLECTION_PIPELINE_RUNS).\
        document(run_id)
    run_doc_dict = run_doc_ref.get().to_dict()
    return run_doc_dict[database_schema.COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID]
