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

# pylint: disable=abstract-method
class GetPointKeysByBatch(beam.DoFn):
    """Queries the project's database to get all point keys from
    database_schema.COLLECTION_IMAGES.

    Input:
       integer index.

    Output:
        point key for each image, label and precision.

    """
    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, index):
        """Queries firestore database for all images within a random range (by batch).
        For each Image found, for each label recognized in the image and for each
        precision level from 4 to 11 a point key is created.

        Args:
            index: the index for querying the database by the random field.

        Yields:
            a point key with count 1 for each image, label and percision.
            point key: (precision, label, quantized coordinates).

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
            if database_schema.COLLECTION_IMAGES_FIELD_LABELS in doc_dict:
                for label in doc_dict[database_schema.COLLECTION_IMAGES_FIELD_LABELS]:
                    for precision in range(4, 11):
                        point_key = (precision, label, _get_quantize_coords_from_geohash(precision,\
                            doc_dict[database_schema.COLLECTION_IMAGES_FIELD_HASHMAP]))
                        yield (point_key, 1)

def _get_quantize_coords_from_geohash(precision, geohash_map):
    """ Returns the quantized coordinates for image's coordinates in the requested precision.

    """
    precision_string = 'hash{precision}'.format(precision=precision)
    lat, lng = geohash2.decode(geohash_map[precision_string])
    return (float(lat), float(lng))

# pylint: disable=abstract-method
class UpdateHeatmapDatabase(beam.DoFn):
    """ Updates Firestore Database according to the weighted points.
        Adds new docs to COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS

    Input:
        point key and count

    """

    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.db = initialize_db()

    # pylint: disable=arguments-differ
    def process(self, point_key_and_count):
        """ Updates the Firestore database after combining all point keys.

            Args:
                point_key_and_count: (point_key, count).
                    point_key: (precision, label, quantized_coordinates).
                    count: the weight of each point key.

        """
        point_key = point_key_and_count[0]
        count = point_key_and_count[1]
        precision_string_id = 'precision{precision_number}'.format(precision_number=point_key[0])
        label = point_key[1]
        quantized_coords = point_key[2]
        quantized_coords_lat = quantized_coords[0]
        quantized_coords_lng = quantized_coords[1]
        geo_point_quantized_coords = firestore.GeoPoint(quantized_coords_lat, quantized_coords_lng)
        self.db.collection(database_schema.COLLECTION_HEATMAP).document(precision_string_id).\
            collection(database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS).\
                document().set({
                    database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_LABEL_ID:\
                        label,
                    database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_COORDINATES:\
                        geo_point_quantized_coords,
                    database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_WEIGHT: count,
                    database_schema.COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_HASHMAP:\
                        get_geo_hashes_map(quantized_coords_lat, quantized_coords_lng)
                })
