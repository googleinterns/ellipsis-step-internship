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

/*Calculates the radius of the circle that contains the current map bounderies*/
function getRadius(
  centerLat: number,
  centerLng: number,
  northEastLat: number,
  northEastLng: number
): number {
  const r = 3963.0; //radius of the earth in miles
  const centerLatR = toRadian(centerLat);
  const centerLngR = toRadian(centerLng);
  const NortheastLatR = toRadian(northEastLat);
  const NortheastLngR = toRadian(northEastLng);
  const dis =
    r *
    Math.acos(
      Math.sin(centerLatR) * Math.sin(NortheastLatR) +
        Math.cos(centerLatR) *
          Math.cos(NortheastLatR) *
          Math.cos(NortheastLngR - centerLngR)
    );
  return dis;
}

function toRadian(decDeg: number): number {
  return decDeg / 57.2958;
}

export { getRadius };
