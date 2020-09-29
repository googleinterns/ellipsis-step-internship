/*
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

export class MergeLists {
  getMinBy: (object: any) => number;

  constructor(getMinBy: (object: any) => number) {
    this.getMinBy = getMinBy;
  }

  getMin(arrayOfLists: any[][], pointers: number[]) {
    let minValue = Infinity;
    let minObject = null;
    let indexOfMin = 0;
    for (let i = 0; i < arrayOfLists.length; i++) {
      const pointer = pointers[i];
      const object = arrayOfLists[i][pointer];
      if (object) {
        if (this.getMinBy(object) < minValue) {
          minObject = object;
          indexOfMin = i;
          minValue = this.getMinBy(object);
        }
      }
    }
    return { object: minObject, index: indexOfMin };
  }
}
