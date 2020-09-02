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
import { expect } from "chai";
import "mocha";
import firebase from "firebase";

describe("get coordinates by qeury", () => {
  const lat = 37.780501;
  const lon = -122.391281;
  const center = new firebase.firestore.GeoPoint(lat, lon);
  const radius = 100;
  const year = 2015;
  const month = 4;
  const day = 20;
  const label = ["cat"];
  it("test by date", () => {
    queryDB
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
  it("test by label", () => {
    queryDB
      .getQueriedCollection(center, radius, label)
      .get()
      .then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
          expect(doc.data().labels).to.contain(label[0]);
        });
      });
  });
  it("test by date and label", () => {
    queryDB
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
  it("test by several labels", () => {
    const labels = ["cat", "bag"];
    queryDB
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
  it("test by center and radius", () => {
    queryDB
      .getQueriedCollection(center, radius, label, year, month, day)
      .get()
      .then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
          expect(doc.distance).to.be.at.least(0);
          expect(doc.distance).to.be.at.most(radius);
        });
      });
  });
  it("test by all arguments", () => {
    queryDB
      .getQueriedCollection(center, radius, label, year, month, day)
      .get()
      .then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
          expect(doc.distance).to.be.at.least(0);
          expect(doc.distance).to.be.at.most(radius);
          expect(doc.data().labels).to.include.members(label);
          expect(doc.data().year).to.equal(2015);
          expect(doc.data().month).to.equal(4);
          expect(doc.data().day).to.equal(20);
        });
      });
  });
});
