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
from google.cloud import firestore
import geohash2
from backend_jobs.pipeline_utils.firestore_database import initialize_db, RANGE_OF_BATCH
from backend_jobs.pipeline_utils import database_schema
from backend_jobs.pipeline_utils.utils import get_geo_hashes_map

ZOOM_TO_PRECISION = {0:4, 1:4, 2:5, 3:5, 4:5, 5:6, 6:6, 7:7, 8:7,\
    9:7, 10:8, 11:8, 12:9, 13:9, 14:9, 15:10, 16:10, 17:11, 18:11, 19:11}

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
    def process(self, index):
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
        query = self.db.collection(database_schema.COLLECTION_IMAGES)\
            .where(database_schema.COLLECTION_IMAGES_FIELD_RANDOM, u'>=', random_min)\
                        .where(database_schema.COLLECTION_IMAGES_FIELD_RANDOM,\
                            u'<', random_max).stream()
        for doc in query:
            doc_dict = doc.to_dict()
            for label in doc_dict[database_schema.COLLECTION_IMAGES_FIELD_LABELS]:
                for precision in range(4, 12):
                    point_key = (precision, label, get_quantize_coords_from_geohash(precision,\
                        doc_dict[database_schema.COLLECTION_IMAGES_FIELD_HASHMAP]))
                    yield (point_key, 1)

def get_quantize_coords_from_geohash(precision, geohash_map):
    precision_string = 'hash{precision}'.format(precision=precision)
    lat, lng = geohash2.decode(geohash_map[precision_string])
    return {'latitude':lat, 'longitude':lng}

# pylint: disable=abstract-method
class UpdateDatabase(beam.DoFn):
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
    def process(self, point_key_and_count):
        """ Updates the Firestore database after verifying the labels.
        Updates parent image doc to include the new label ids.
        Updates the label doc to Visible.

            Args:
                label_info: (label doc Python dictionary, list of label ids)

        """
        point_key = point_key_and_count[0]
        count = point_key_and_count[1]
        precision_string_id = 'precision{precision_number}'.format(precision_number=point_key[0])
        label = point_key[1]
        quantized_coords_lat = point_key[2]['latitude']
        quantized_coords_lng = point_key[2]['longtitude']
        quantized_coords = firestore.GeoPoint(quantized_coords_lat, quantized_coords_lng)
        self.db.collection(database_schema.COLLECTION_HEATMAP).document(precision_string_id).\
            collection(database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS).\
                document().set({
                    database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_LABEL_ID:\
                        label,
                    database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_QUANTIZED_COORDINATES:\
                        quantized_coords,
                    database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_WEIGHT: count,
                    database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_HASHMAP:\
                        get_geo_hashes_map(quantized_coords_lat, quantized_coords_lng)
                })
