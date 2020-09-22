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

import * as geoquery from "../src/geoquery";
import { expect } from "chai";
import { hash } from "geokit";
import "mocha";

describe("query by geohash of bounderies", () => {
  it("contains all random points", () => {
    const northEast = { lat: 37.826683863620005, lng: -122.33592020593264 };
    const center = { lat: 37.78048656364348, lng: -122.39128100000002 };
    const southWest = { lat: 37.73428926366695, lng: -122.4466417940674 };
    const maxLat = northEast.lat;
    const minLat = southWest.lat;
    const maxLng = northEast.lng;
    const minLng = southWest.lng;
    const geohashList = geoquery.getGeohashBoxes(northEast, center, southWest);
    const geohashPrecision = geohashList[0].length;
    for (let i = 0; i < 100; i++) {
      const newGeohash = hash(getRandomCoords(maxLat, minLat, maxLng, minLng));
      expect(geohashList).to.include(newGeohash.substring(0, geohashPrecision));
    }
  });
});

function getRandomCoords(
  maxLat: number,
  minLat: number,
  maxLng: number,
  minLng: number
) {
  const lat = Math.random() * (maxLat - minLat) + minLat;
  const lng = Math.random() * (maxLng - minLng) + minLng;
  return { lat: lat, lng: lng };
}
