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

# pylint: disable=abstract-method
class RedefineLabels(beam.DoFn):
    """Converts parallelly the labels list returned from
    the provider to the corresponding label Id's.

    """

    # pylint: disable=arguments-differ
    def process(self, element, redefine_map):
        """Uses the global redefine map to change the different labels to the project's label Ids.

        Args:
            element: tuple of dictionary of image properties and list of labels.
            provider_id: image recognition provider for the redefine map.

        Returns:
            [(dictionary of image properties, label ids list)]
        """
        all_labels_and_ids = []
        for label in element[1]:
            # redefine_map = get_redefine_map(provider_id)
            if label in redefine_map:
                for label_id in redefine_map[label]:
                    all_labels_and_ids.append({'name': label, 'id': label_id})
            else:
                all_labels_and_ids.append({'name': label})
        return [(element[0], all_labels_and_ids)]
