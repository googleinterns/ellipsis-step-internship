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
  it("the boundary box of geohash of precision 7 contains all random points", () => {
    const northEast = { lat: 34.45348076460549, lng: 35.84213872886295 };
    const southWest = { lat: 34.45197457553289, lng: 35.84040870404834 };
    const maxLat = northEast.lat;
    const minLat = southWest.lat;
    const maxLng = northEast.lng;
    const minLng = southWest.lng;
    const geohashList = geoquery.getGeohashBoxes(northEast, southWest);
    const geohashPrecision = geohashList[0].length;
    for (let i = 0; i < 100; i++) {
      const newGeohash = hash(getRandomCoords(maxLat, minLat, maxLng, minLng));
      expect(geohashList).to.include(newGeohash.substring(0, geohashPrecision));
    }
  });
  it("the boundary box of geohash of precision 4 contains all random points", () => {
    const northEast = { lat: 37.826683863620005, lng: -122.33592020593264 };
    const southWest = { lat: 37.73428926366695, lng: -122.4466417940674 };
    const maxLat = northEast.lat;
    const minLat = southWest.lat;
    const maxLng = northEast.lng;
    const minLng = southWest.lng;
    const geohashList = geoquery.getGeohashBoxes(northEast, southWest);
    const geohashPrecision = geohashList[0].length;
    for (let i = 0; i < 100; i++) {
      const newGeohash = hash(getRandomCoords(maxLat, minLat, maxLng, minLng));
      expect(geohashList).to.include(newGeohash.substring(0, geohashPrecision));
    }
  });
  it("the boundary box of geohash of precision 1 contains all random points", () => {
    const northEast = { lat: 68.89239418761491, lng: 43.79792797674112 };
    const southWest = { lat: 34.19175837616178, lng: -12.891525148258877 };
    const maxLat = northEast.lat;
    const minLat = southWest.lat;
    const maxLng = northEast.lng;
    const minLng = southWest.lng;
    const geohashList = geoquery.getGeohashBoxes(northEast, southWest);
    const geohashPrecision = geohashList[0].length;
    for (let i = 0; i < 100; i++) {
      const newGeohash = hash(getRandomCoords(maxLat, minLat, maxLng, minLng));
      expect(geohashList).to.include(newGeohash.substring(0, geohashPrecision));
    }
  });
  it("does not query by geohash if the boundaries are wider than 1/36 of the world", () => {
    const northEast = { lat: 50.63354150815655, lng: -108.06344912811238 };
    const southWest = { lat: -0.9534027632326522, lng: -164.75290225311238 };
    const geohashList = geoquery.getGeohashBoxes(northEast, southWest);
    expect(geohashList).to.be.empty;
  });
});

describe("check function removeDuplicates", () => {
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  it("case 1- array contains duplicates", () => {
    const result = geoquery.removeDuplicates(["a", "a", "a", "a"]);
    expect(result).to.eql(["a"]);
  });
  it("case 2- array contains substrings", () => {
    const result = geoquery.removeDuplicates(["aab", "aacc", "aa", "aaad"]);
    expect(result).to.eql(["aa"]);
  });
  it("case 3- array contains nothing", () => {
    const result = geoquery.removeDuplicates([]);
    expect(result).to.eql([]);
  });
  it("case 3- array contains duplicates and substrings", () => {
    const result = geoquery.removeDuplicates(["ab", "abc", "aaa", "aa", "abc"]);
    expect(result).to.eql(["ab", "aa"]);
  });
});

describe("check function getGeohashBoxes hashList", () => {
  const northEast = { lat: 37.826683863620005, lng: -122.33592020593264 };
  const southWest = { lat: 37.73428926366695, lng: -122.4466417940674 };
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  it("case 1- check langth of list", () => {
    const result = geoquery.getGeohashBoxes(northEast, southWest).length;
    expect(result).to.be.at.least(0);
    expect(result).to.be.at.least(4);
  });
  it("case 2- check that all hashes are the same length", () => {
    const geolist = geoquery.getGeohashBoxes(northEast, southWest);
    geolist.forEach((geohash) => {
      const result = geohash.length;
      expect(result).to.equal(4);
    });
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
