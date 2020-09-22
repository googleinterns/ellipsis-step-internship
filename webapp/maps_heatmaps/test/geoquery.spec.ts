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
import "mocha";

/*("query by geohash of bounderies", () => {
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  it("containsop all random points", () => {});
});*/

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
