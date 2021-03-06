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

import * as queryDB from "../src/queryDB";
import { expect } from "chai";
import "mocha";
import { DateTime } from "../src/interface";

describe("check function getQueriedCollection", () => {
  const hash = "9q8y";
  const datetime: DateTime = { year: 2015, month: 4, day: 20 };
  const label = ["cat"];
  it("test by date", async () => {
    await queryDB
      .getQueriedCollection(label, datetime, hash)
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
      .getQueriedCollection(label, {}, hash)
      .get()
      .then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
          expect(doc.data().labels).to.contain(label[0]);
        });
      });
  });
  it("test by date and label", async () => {
    await queryDB
      .getQueriedCollection(label, datetime, hash)
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
      .getQueriedCollection(labels, datetime, hash)
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
});
