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
import { toRadian, getRadius } from "./utils";
import { expect } from "chai";
import "mocha";

describe("toRadian function", () => {
  it("correctly converts", () => {
    const value1 = 10;
    const result = toRadian(value1);
    expect(result).to.equal(value1 / 57.2958);
  });
  it("correctly converts from 0", () => {
    const value1 = 0;
    const result = toRadian(value1);
    expect(result).to.equal(value1 / 57.2958);
  });
  it("correctly converts a floating point", () => {
    const value1 = 10.11;
    const result = toRadian(value1);
    expect(result).to.equal(value1 / 57.2958);
  });
});
