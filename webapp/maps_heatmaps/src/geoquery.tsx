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
import { map } from "./index";
let rectangles: google.maps.Rectangle[] = [];

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
  console.log(Array.from(new Set(newHashs)));
  return Array.from(new Set(newHashs));
}

function bounds(geohash: string) {
  const base32 = "0123456789bcdefghjkmnpqrstuvwxyz";

  let evenBit = true;
  let latMin = -90;
  let latMax = 90;
  let lonMin = -180;
  let lonMax = 180;

  for (let i = 0; i < geohash.length; i++) {
    const chr = geohash.charAt(i);
    const idx = base32.indexOf(chr);
    if (idx == -1) throw new Error("Invalid geohash");

    for (let n = 4; n >= 0; n--) {
      const bitN = (idx >> n) & 1;
      if (evenBit) {
        // longitude
        const lonMid = (lonMin + lonMax) / 2;
        if (bitN == 1) {
          lonMin = lonMid;
        } else {
          lonMax = lonMid;
        }
      } else {
        // latitude
        const latMid = (latMin + latMax) / 2;
        if (bitN == 1) {
          latMin = latMid;
        } else {
          latMax = latMid;
        }
      }
      evenBit = !evenBit;
    }
  }

  const bounds = { north: latMax, south: latMin, east: lonMax, west: lonMin };
  return bounds;
}

function eraseAllRectangles(): void {
  rectangles.forEach((rectangle) => {
    rectangle.setMap(null);
  });
  rectangles = [];
}

function addRetangle(geohash: string) {
  const rec = new google.maps.Rectangle({
    map: map,
    bounds: bounds(geohash),
    fillColor: "#FF0000",
    fillOpacity: 0.35,
  });
  rectangles.push(rec);
}

function addMarker(cord: google.maps.LatLng) {
  new google.maps.Marker({
    position: cord,
    map: map,
  });
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
  geohashList = geohashList.concat(
    getCommonGeohash(northEast, eastCenter, southEast),
    getCommonGeohash(northWest, westCenter, southWest),
    getCommonGeohash(northEast, northCenter, northWest),
    getCommonGeohash(southEast, southCenter, southWest)
  );
  console.log(geohashList);
  return removeDuplicates(geohashList);
}

function getCommonGeohash(
  cornerA: { lat: number; lng: number },
  middle: { lat: number; lng: number },
  cornerB: { lat: number; lng: number }
): string[] {
  const cornerAHash = hash(cornerA);
  const middleHash = hash(middle);
  const cornerBHash = hash(cornerB);
  console.log(cornerAHash + " " + cornerBHash + " " + middleHash);
  const commonPrefixLenA = getLongestCommonPrefixLen(cornerAHash, middleHash);
  const commonPrefixLenB = getLongestCommonPrefixLen(cornerBHash, middleHash);
  const maxDiff = Math.max(commonPrefixLenA, commonPrefixLenB);
  console.log(commonPrefixLenA, commonPrefixLenB, maxDiff);
  console.log(
    cornerAHash.substring(0, maxDiff) + " " + cornerBHash.substring(0, maxDiff)
  );
  return [cornerAHash.substring(0, maxDiff), cornerBHash.substring(0, maxDiff)];
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
