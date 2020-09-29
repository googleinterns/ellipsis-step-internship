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

export class MinOfLists<T> {
  getMinByFunction: (object: T) => number;

  constructor(getMinBy: (object: T) => number) {
    this.getMinByFunction = getMinBy;
  }

  /*@param arrayOfLists is an array the contains all list which we need to retrieve the minimum from
    @param pointers for the minimum object of each list in the arrayOflists  
    @return map of the minimun object that is found by the getMinByFuction of the class,
    and the number of list in which the minimum object is found,*/
  getMin(
    arrayOfLists: T[][],
    pointers: number[]
  ): { object: T | null; index: number } {
    let minValue = Infinity;
    let minObject = null;
    let indexOfMin = 0;
    for (let i = 0; i < arrayOfLists.length; i++) {
      const pointer = pointers[i];
      const object = arrayOfLists[i][pointer];
      if (object != null) {
        if (this.getMinByFunction(object) < minValue) {
          minObject = object;
          indexOfMin = i;
          minValue = this.getMinByFunction(object);
        }
      }
    }
    return { object: minObject, index: indexOfMin };
  }
}
