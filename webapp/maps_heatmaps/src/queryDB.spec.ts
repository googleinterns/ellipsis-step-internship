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

import * as queryDB from "./queryDB";
import * as geohash from "ngeohash";
import { expect } from "chai";
import "mocha";
import firebase from "firebase";

describe("check function getQueriedCollection", () => {
  const lat = 37.780501;
  const lon = -122.391281;
  const center = new firebase.firestore.GeoPoint(lat, lon);
  const radius = 100;
  const year = 2015;
  const month = 4;
  const day = 20;
  const label = ["cat"];
  it("test by date", async () => {
    await queryDB
      .getQueriedCollection(center, radius, label, year, month, day)
      .get()
      .then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
          expect(doc.data().year).to.equal(2015);
          expect(doc.data().month).to.equal(4);
          expect(doc.data().day).to.equal(20);
        });
      });
  });
  it("test by label", async () => {
    await queryDB
      .getQueriedCollection(center, radius, label)
      .get()
      .then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
          expect(doc.data().labels).to.contain(label[0]);
        });
      });
  });
  it("test by date and label", async () => {
    await queryDB
      .getQueriedCollection(center, radius, label, year, month, day)
      .get()
      .then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
          expect(doc.data().labels).to.contain(label[0]);
          expect(doc.data().year).to.equal(2015);
          expect(doc.data().month).to.equal(4);
          expect(doc.data().day).to.equal(20);
        });
      });
  });
  it("test by several labels", async () => {
    const labels = ["cat", "bag"];
    await queryDB
      .getQueriedCollection(center, radius, labels, year, month, day)
      .get()
      .then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
          expect(labels).to.include.members(doc.data().labels);
          expect(doc.data().year).to.equal(2015);
          expect(doc.data().month).to.equal(4);
          expect(doc.data().day).to.equal(20);
        });
      });
  });
  it("test by center and radius", async () => {
    await queryDB
      .getQueriedCollection(center, radius, label)
      .get()
      .then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
          expect(doc.distance).to.be.at.least(0);
          expect(doc.distance).to.be.at.most(radius);
        });
      });
  });
});

describe("convert latlon to geohash function", () => {
  it("correctly converts", () => {
    const lat = 70.2995;
    const lng = -27.9993;
    const result = geohash.encode(lat, lng, 12);
    expect(result).to.equal("gkkpfves308e");
  });
  it("correctly converts", () => {
    const lat = -70.2995;
    const lng = 27.9993;
    const result = geohash.encode(lat, lng, 12);
    expect(result).to.equal("heebj4k7wzrk");
  });
  it("correctly converts", () => {
    const lat = -120.9734865;
    const lng = 37.675654;
    const result = geohash.encode(lat, lng, 12);
    expect(result).to.equal("hb4b1248425b");
  });
  it("correctly converts", () => {
    const lat = 120.9734865;
    const lng = 37.675654;
    const result = geohash.encode(lat, lng, 12);
    expect(result).to.equal("uzfzcrfxfrgz");
  });
  it("correctly converts", () => {
    const lat = -120.9734865;
    const lng = -37.675654;
    const result = geohash.encode(lat, lng, 12);
    expect(result).to.equal("50j0n8j2j8h0");
  });
  it("correctly converts", () => {
    const lat = 0.0;
    const lng = 0.0;
    const result = geohash.encode(lat, lng, 12);
    expect(result).to.equal("s00000000000");
  });
  it("correctly converts", () => {
    const lat = 120.0;
    const lng = 0.0;
    const result = geohash.encode(lat, lng, 12);
    expect(result).to.equal("upbpbpbpbpbp");
  });
});
