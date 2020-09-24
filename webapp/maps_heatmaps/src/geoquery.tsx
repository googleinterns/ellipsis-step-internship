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

function removeDuplicates(hashs: string[]): string[] {
  const newHashs: string[] = [];
  let subString = false;
  hashs.map((hash) => {
    newHashs.forEach((hash1, index1) => {
      if (hash1.startsWith(hash)) {
        newHashs[index1] = hash;
        subString = true;
      }
      if (hash.startsWith(hash1)) subString = true;
    });
    if (!subString) newHashs.push(hash);
    subString = false;
  });
  //console.log(Array.from(new Set(newHashs)));
  return Array.from(new Set(newHashs));
}

function getGeohashBoxes(
  northEast: { lat: number; lng: number },
  center: { lat: number; lng: number },
  southWest: { lat: number; lng: number }
): string[] {
  let geohashList: string[] = [];
  const northWest = { lat: northEast.lat, lng: southWest.lng };
  const southEast = { lat: southWest.lat, lng: northEast.lng };
  const northCenter = { lat: northEast.lat, lng: center.lng };
  const southCenter = { lat: southWest.lat, lng: center.lng };
  const eastCenter = { lat: center.lat, lng: northEast.lng };
  const westCenter = { lat: center.lat, lng: southWest.lng };
  try {
    geohashList = geohashList.concat(
      getCommonGeohash(northEast, eastCenter, southEast),
      getCommonGeohash(northWest, westCenter, southWest),
      getCommonGeohash(northEast, northCenter, northWest),
      getCommonGeohash(southEast, southCenter, southWest)
    );
    return removeDuplicates(geohashList);
  } catch (e) {
    return [];
  }
}

function getCommonGeohash(
  cornerA: { lat: number; lng: number },
  middle: { lat: number; lng: number },
  cornerB: { lat: number; lng: number }
): string[] {
  const cornerAHash = hash(cornerA);
  const middleHash = hash(middle);
  const cornerBHash = hash(cornerB);
  const commonPrefixLenA = getLongestCommonPrefixLen(cornerAHash, middleHash);
  const commonPrefixLenB = getLongestCommonPrefixLen(cornerBHash, middleHash);
  const commonPrefixMaxLen = Math.max(commonPrefixLenA, commonPrefixLenB);
  if (commonPrefixMaxLen === 0) throw new Error("no common prefix");
  return [
    cornerAHash.substring(0, commonPrefixMaxLen),
    cornerBHash.substring(0, commonPrefixMaxLen),
  ];
}

function getLongestCommonPrefixLen(hash1: string, hash2: string): number {
  let count = 0;
  let i = 0;
  while (hash1.charAt(i) === hash2.charAt(i)) {
    i++;
    count++;
  }
  return count;
}

export { getGeohashBoxes, removeDuplicates };
