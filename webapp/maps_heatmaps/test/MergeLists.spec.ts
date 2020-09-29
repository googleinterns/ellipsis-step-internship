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

import { expect } from "chai";
import "mocha";
import { MergeLists } from "../src/MergeLists";

describe("check class MergeLists", () => {
  it("case 1- minimum number is a positive", async () => {
    const getMinObject = new MergeLists((doc: number) => doc);
    const minInfo = getMinObject.getMin(
      [[7, 9], [1], [3, 2], [4]],
      [0, 0, 1, 0]
    );
    const minDoc = minInfo.object;
    const numOfList = minInfo.index;
    expect(minDoc).to.equal(1);
    expect(numOfList).to.equal(1);
  });
  it("case 2- minimum number is a negative", async () => {
    const getMinObject = new MergeLists((doc: number) => doc);
    const minInfo = getMinObject.getMin(
      [[1, 2, 3], [0], [-3], [4]],
      [0, 0, 0, 0]
    );
    const minDoc = minInfo.object;
    const numOfList = minInfo.index;
    expect(minDoc).to.equal(-3);
    expect(numOfList).to.equal(2);
  });
  it("case 3- minimum number is a zero", async () => {
    const getMinObject = new MergeLists((doc: number) => doc);
    const minInfo = getMinObject.getMin(
      [[1, 2, 3], [0], [-3], [4]],
      [0, 0, 0, 0]
    );
    const minDoc = minInfo.object;
    const numOfList = minInfo.index;
    expect(minDoc).to.equal(-3);
    expect(numOfList).to.equal(2);
  });
});
