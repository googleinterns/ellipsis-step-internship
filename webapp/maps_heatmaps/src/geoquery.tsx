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

import { hash } from "geokit";
import { LatLng } from "./interface";
import { findMidCoordinates } from "./utils";

/*@param hashes an array of 8 geohash strings that represents
 the geohashes that cover the visible map from all sides.
  @return an array of 1-4 geohash strings that cover the visible map with no duplicates. */
function removeDuplicates(hashes: string[]): string[] {
  const newHashes: string[] = [];
  let subString = false;
  hashes.map((hash) => {
    newHashes.forEach((hash1, index1) => {
      if (hash1.startsWith(hash)) {
        newHashes[index1] = hash;
        subString = true;
      }
      if (hash.startsWith(hash1)) subString = true;
    });
    if (!subString) newHashes.push(hash);
    subString = false;
  });
  return Array.from(new Set(newHashes));
}

/*@return an array of maximum 4 geohash boxes that cover the whole visible map.
  The geohash strings that are returned are the most specific 0-4 geohashes 
  that cover the whole visible map. */
function getGeohashBoxes(northEast: LatLng, southWest: LatLng): string[] {
  let geohashList: string[] = [];
  const northWest = { lat: northEast.lat, lng: southWest.lng };
  const southEast = { lat: southWest.lat, lng: northEast.lng };
  try {
    geohashList = geohashList.concat(
      getMostSpecificGeohashesCover(northEast, southEast),
      getMostSpecificGeohashesCover(northWest, southWest),
      getMostSpecificGeohashesCover(northEast, northWest),
      getMostSpecificGeohashesCover(southEast, southWest)
    );
    return removeDuplicates(geohashList);
  } catch (e) {
    //If the area on the visible map is more than 1/36 of the world.
    return [];
  }
}

/*@return an array of 1-2 different geohash boxes that cover a side of 
  the visible map. 
  For Each side the function compares between the geohash strings of the
  two corners and the one of the middle point and finds the longest common
  prefix of the two comparisons. This prefix and the prefix of theb same 
  length of the other corner represent the most specific geohash boxes that
  cover this side of the visible map. */
function getMostSpecificGeohashesCover(
  cornerA: LatLng,
  cornerB: LatLng
): string[] {
  const middle = findMidCoordinates(cornerA, cornerB);
  const cornerAHash = hash(cornerA);
  const middleHash = hash(middle);
  const cornerBHash = hash(cornerB);
  const commonPrefixLenA = getCommonPrefixLen(cornerAHash, middleHash);
  const commonPrefixLenB = getCommonPrefixLen(cornerBHash, middleHash);
  const commonPrefixMaxLen = Math.max(commonPrefixLenA, commonPrefixLenB);
  if (commonPrefixMaxLen === 0) throw new Error("no common prefix");
  return [
    cornerAHash.substring(0, commonPrefixMaxLen),
    cornerBHash.substring(0, commonPrefixMaxLen),
  ];
}

function getCommonPrefixLen(hash1: string, hash2: string): number {
  let count = 0;
  while (hash1.charAt(count) === hash2.charAt(count)) {
    count++;
  }
  return count;
}

export { getGeohashBoxes, removeDuplicates };
