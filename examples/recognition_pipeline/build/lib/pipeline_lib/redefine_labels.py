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

# TODO: Think about whether to do this in the same map, or change to ids inside the redefine method.
LABEL_TO_ID = {'bag': 'GaveDiWni9CzOp6eYRDE'}
REDEFINE_LABELS = {'Google_Vision_API':{'Bag': LABEL_TO_ID['bag'], 'Glass': LABEL_TO_ID['bag']}} #TODO: fill this map, need to think how do to that. 

class RedefineLabels(beam.DoFn):
    """Converts parallelly the labels list returned from the provider to the corresponding label Id's.

    """
    def process(self, element, provider):
        """Uses the global redefine map to change the different labels to the project's label Ids.

        Args:
            element: (dictionary of image properties, labels list)
            provider: image recognition provider for the redefine map

        Returns:
            [(dictionary of image properties, label ids list)] 
        """
        all_label_Ids = []
        for label in element[1]:
            if label in REDEFINE_LABELS[provider]: 
                labelId = REDEFINE_LABELS[provider][label]
                all_label_Ids.append(labelId)
        if all_label_Ids:
            return [(element[0], all_label_Ids)]