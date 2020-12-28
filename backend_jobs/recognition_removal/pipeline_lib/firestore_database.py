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
from itertools import chain
import apache_beam as beam
from backend_jobs.pipeline_utils.firestore_database import initialize_db, RANGE_OF_BATCH
from backend_jobs.pipeline_utils import database_schema, data_types
from backend_jobs.pipeline_utils.utils import get_query_from_heatmap_collection,\
    get_quantize_coords_from_geohash


# pylint: disable=abstract-method
class GetAndDeleteBatchedLabelsDataset(beam.DoFn):
    """Queries the project's database to get the labels dataset to remove,
    and deletes the documents from the database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS.

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
    def process(self, index, recognition_provider = None, recognition_run = None):
        """Queries firestore database for labels recognized by the given
        recognition provider or run and deletes the documents from the
        database (by batch).

        Args:
            index: the index for querying the database by the random field.
            recognition_provider: the input of the pipeline, determines the labels dataset.
            recognition_run: the input of the pipeline, determines the labels dataset.

        Yields:
            A tuple of a Python dictionary with all the information (fields and id)
            of each one of the Firestore query's label documents as stored in
            the database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS.
            yields (image_id, label info dict)

        Raises:
            Value error if both recognition_provider and recognition_run
            are not None or both are None.

        """
        if recognition_provider and recognition_run:
            raise ValueError('both recognition provider and run are provided -\
                one should be provided')
        if not recognition_provider and not recognition_run:
            raise ValueError('both recognition provider and run are not provided -\
                one should be provided')
        # The lower limit for querying the database by the random field.
        random_min = index * RANGE_OF_BATCH
        # The higher limit for querying the database by the random field.
        random_max = random_min + RANGE_OF_BATCH
        if recognition_provider:
            query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS\
                ).where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PROVIDER_ID,\
                    u'==', recognition_provider.lower()).where(database_schema.\
                        COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_RANDOM, u'>=', random_min).\
                            where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_RANDOM,\
                                u'<', random_max).stream()
        else:
            query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS).\
                where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PIPELINE_RUN_ID,\
                    u'==', recognition_run).where(database_schema.\
                        COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_RANDOM, u'>=', random_min)\
                            .where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_RANDOM,\
                                u'<', random_max).stream()
        for doc in query:
            doc_dict = doc.to_dict()
            if database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_IDS in doc_dict:
                # Only label documents with a 'Label Ids' field are relevant for the
                # pipeline's continuation. The documents will be used to delete the
                # label ids from the parent image 'labels' array if needed.
                parent_image_id =\
                    doc_dict[database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PARENT_IMAGE_ID]
                label_ids =\
                    doc_dict[database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_IDS]
                yield (parent_image_id, label_ids)
            doc.reference.delete() # Delete label doc from database.

    # pylint: disable=abstract-method
class UpdateLabelsInImageDocs(beam.DoFn):
    """Updates the labels field in all image douments in the
       database_schema.COLLECTION_IMAGES.

       Input: a tuple of parent image doc id and a
       list of all label ids that were deleted in the parent image doc.
       (image_doc, list_of_labels)

       Output: point keys which are used to update database_schema.COLLECTION_HEATMAP
               according to removed labels.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, image_and_labels):
        """
        Checks if there are any other label docs in each image's
        database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS
        that contain the label ids that were deleted.
        If not - deletes the corresponding label id from the 'labels' array field in the
        image document in database_schema.COLLECTION_IMAGES.
        For each label deleted, the method updates database_schema.COLLECTION_HEATMAP
        and decreases the weight of the point keys for each precision.

        Args:
            image_and_labels: (parent image doc, list of lists of label ids)
        
        Yields:
            (point key, 1).
            point key: (precision, label id, quantized coordinates).
            A point key for each label which was removed from the image
            and for each precision from 4 to 12. The quantized coordinates are
            calculated from the parent image's hashmap.

        """
        parent_image_id = image_and_labels[0]
        label_ids_lists = image_and_labels[1]
        label_ids = union(label_ids_lists)
        parent_image_ref = self.db.collection(database_schema.COLLECTION_IMAGES).\
            document(parent_image_id)
        geohash_map = parent_image_ref.get().to_dict()[database_schema.COLLECTION_IMAGES_FIELD_HASHMAP]
        for label_id in label_ids:
            query = self.db.collection_group(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS\
                ).where(database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PARENT_IMAGE_ID\
                    ,u'==', parent_image_id).where(database_schema.\
                        COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_IDS,\
                            u'array_contains', label_id).where(\
                                database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_VISIBILITY,\
                                    u'==', data_types.VisibilityType.VISIBLE.value)
            if len(query.get()) == 0: # No doc of the label id was found.
                self._delete_label_id_from_labels_array(parent_image_ref, label_id)
                for precision in range(4, 12): # Get point keys for next pipeline steps.
                    point_key = (precision, label_id, get_quantize_coords_from_geohash(\
                        precision, geohash_map))
                    yield (point_key, 1)
            
    def _delete_label_id_from_labels_array(self, image_doc_ref, label_id):
        image_doc_dict = image_doc_ref.get().to_dict()
        labels_array = image_doc_dict[database_schema.COLLECTION_IMAGES_FIELD_LABELS]
        if label_id in labels_array:
            labels_array.remove(label_id)
        image_doc_ref.update({
            database_schema.COLLECTION_IMAGES_FIELD_LABELS: labels_array
        })

class UpdateHeatmapDatabase(beam.DoFn):
    """Updates the database_schema.COLLECTION_HEATMAP to not include
       the removed labels.

       Input: (point key, count)

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, point_key_and_count):
        """ Queries the Firestore database after combining all point keys
        and updates accordingly. If count == current weight, the weighted point's
        doc will be deleted. If not, count will be decreased from weight.
            

        Args:
            point_key_and_count: (point_key, count).
                point_key: (precision, label, quantized_coordinates).
                count: the weight of each deleted point key.

        """
        point_key = point_key_and_count[0]
        count = point_key_and_count[1]
        label = point_key[1]
        quantized_coords = point_key[2]
        query = get_query_from_heatmap_collection(self.db, label, quantized_coords)
        for doc in query:
            doc_dict = doc.to_dict()
            point_weight = doc_dict[\
                database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_WEIGHT]
            if point_weight == count:
                doc.reference.delete()
            else:
                point_weight -= count
                doc.reference.update({
                    database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_WEIGHT:\
                        point_weight,
                    })

def union(list_of_lists):
    """ Returns a list which is the union of all lists in
    list_of_lists.

    """
    all_labels = set(chain.from_iterable(list_of_lists))
    return list(all_labels)


def update_pipelinerun_doc_to_invisible(pipeline_run_id):
    """ Updates the pipeline run's document in the Pipeline runs Firestore collection
    to invisible after the labels were removed.

    """
    doc_ref = initialize_db().collection(database_schema.COLLECTION_PIPELINE_RUNS).\
        document(pipeline_run_id)
    doc_ref.update({
            database_schema.COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_VISIBILITY:\
                data_types.VisibilityType.INVISIBLE.value
        })
