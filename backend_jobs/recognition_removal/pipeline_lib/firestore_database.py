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
from backend_jobs.recognition_pipeline.pipeline_lib.firestore_database import add_id_to_dict
from backend_jobs.pipeline_utils import database_schema

RANGE_OF_BATCH = 0.1

# pylint: disable=abstract-method
class GetBatchedDataset(beam.DoFn):
    """Queries the project's database to get the image dataset to label.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element, recognition_provider = None, recognition_run = None):
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
        if recognition_provider and recognition_run:
            raise ValueError('both recognition provider and run are provided - there should be only one')
        # The lower limit for querying the database by the random field.
        random_min = element * RANGE_OF_BATCH
        # The higher limit for querying the database by the random field.
        random_max = random_min + RANGE_OF_BATCH
        if recognition_provider:
            query = self.db.collection_group(u'Labels').\
                where(u'providerId',u'==', recognition_provider.lower()).\
                    where(u'random', u'>=', random_min).where(u'random', u'<', random_max).stream()
        else:
            query = self.db.collection_group(u'Labels').\
                where(u'pipelineRunId', u'==', recognition_run).\
                    where(u'random', u'>=', random_min).where(u'random', u'<', random_max).stream()
        docs_generator = (add_id_to_dict(doc) for doc in query if database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_IDS in add_id_to_dict(doc))
        self._delete_all_docs(query)
        return docs_generator

    def _delete_all_docs(self, firestore_query):
        for doc in firestore_query:
            doc.reference.delete()

    # pylint: disable=abstract-method
class UpdateLabelsInImageDocs(beam.DoFn):
    """Queries the project's database to get the image dataset to label.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, element):
        """Q

        """
        parent_image_id = element[database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PARENT_IMAGE_ID]
        parent_image_ref = self.db.collection(database_schema.COLLECTION_IMAGES).\
            document(parent_image_id)
        label_ids = element[database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_IDS]
        # TODO: make sure only doc with label ids get here
       

        for label_id in label_ids:
            query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS\
                ).where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PARENT_IMAGE_ID, u'==', parent_image_id)\
                    .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_IDS, u'array_contains', label_id)\
                        .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_VISIBILITY, u'==',\
                            database_schema.LABEL_VISIBILITY_VISIBLE)
            if len(query.get()) == 0:
                self._delete_label_id_from_labels_array(parent_image_ref, label_id)
            self._delete_label_id_from_labels_array(parent_image_ref, label_id)

    def _delete_label_id_from_labels_array(self, image_doc_ref, label_id):
        image_doc_dict = image_doc_ref.get().to_dict()
        labels_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_LABELS]
        if label_id in labels_array:
            labels_array.remove(label_id)
        image_doc_ref.update({
            database_schema.COLLECTION_IMAGES_FIELD_LABELS: labels_array
        })
        