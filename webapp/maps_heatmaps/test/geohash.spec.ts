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

import * as geokit from "geokit";
import { expect } from "chai";
import "mocha";

describe("convert latlon to geohash function", () => {
  it("correctly converts - standard coordinates", () => {
    const coordinates = { lat: 70.2995, lng: -27.9993 };
    const result = geokit.hash(coordinates, 12);
    expect(result).to.equal("gkkpfves308e");
  });
  it("correctly converts - standard coordinates", () => {
    const coordinates = { lat: -70.2995, lng: 27.9993 };
    const result = geokit.hash(coordinates, 12);
    expect(result).to.equal("heebj4k7wzrk");
  });
  it("correctly converts - Center", () => {
    const coordinates = { lat: 0, lng: 0 };
    const result = geokit.hash(coordinates, 12);
    expect(result).to.equal("7zzzzzzzzzzz");
  });
  it("correctly converts - South East", () => {
    const coordinates = { lat: -90, lng: 180 };
    const result = geokit.hash(coordinates, 12);
    expect(result).to.equal("pbpbpbpbpbpb");
  });
  it("correctly converts - North East", () => {
    const coordinates = { lat: 90, lng: 180 };
    const result = geokit.hash(coordinates, 12);
    expect(result).to.equal("zzzzzzzzzzzz");
  });
  it("correctly converts - South West", () => {
    const coordinates = { lat: -90, lng: -180 };
    const result = geokit.hash(coordinates, 12);
    expect(result).to.equal("000000000000");
  });
  it("correctly converts - North West", () => {
    const coordinates = { lat: 90, lng: -180 };
    const result = geokit.hash(coordinates, 12);
    expect(result).to.equal("bpbpbpbpbpbp");
  });
});
