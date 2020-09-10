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

// [START maps_layer_heatmap]
// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">

// Imports
let map: google.maps.Map, heatmap: google.maps.visualization.HeatmapLayer;
let selectedLabels: string[] = [];
let selectedYear: number | undefined;
let selectedMonth: number | undefined;

import * as firebase from "firebase";
import * as geofirestore from "geofirestore";
import { database } from "./declareDatabase";
import * as queryDB from "./queryDB";
import React from "react";
import ReactDOM from "react-dom";

import SidePanel from "./components/sidepanel";

getLabelTags();

function getLabelTags() {
  const labelsRef = database.collection("LabelTags");
  const labelTags: Array<Record<string, string>> = [];
  labelsRef.get().then((querySnapshot) => {
    querySnapshot.forEach((doc) => {
      const name = doc.data().name;
      labelTags.push({ value: name, label: name });
    });
    ReactDOM.render(
      <SidePanel labels={labelTags} />,
      document.querySelector("#root")
    );
    selectedLabels = labelTags.map((x: Record<string, string>) => x.label);
  });
}

function initMap(): void {
  map = new google.maps.Map(document.getElementById("map") as HTMLElement, {
    zoom: 13,
    mapTypeId: "satellite",
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
      position: google.maps.ControlPosition.TOP_CENTER,
    },
  });

  // TODO: decide where to set default center.
  const images = database.collection("images");
  images.get().then((querySnapshot) => {
    if (!querySnapshot.empty) {
      const image = querySnapshot.docs[0].data();
      map.setCenter({
        lat: image.coordinates.latitude,
        lng: image.coordinates.longitude,
      });
    }
  });

  heatmap = new google.maps.visualization.HeatmapLayer({
    data: [],
    map: map,
  });
  map.addListener("center_changed", () => mapChanged());
  map.addListener("zoom_changed", () => mapChanged());
}
async function mapChanged() {
  const center: google.maps.LatLng = map.getCenter();
  const lat = center.lat();
  const lng = center.lng();
  const newCenter = new firebase.firestore.GeoPoint(lat, lng);
  const bounds = map.getBounds(); //map's current bounderies
  //TODO: check what should be the default radius value.
  let newRadius = 2;
  if (bounds) {
    const meterRadius = google.maps.geometry.spherical.computeDistanceBetween(
      bounds.getCenter(),
      bounds.getNorthEast()
    );
    newRadius = meterRadius * 0.000621371192; //convert to miles
  }
  const queriedCollection = queryDB.getQueriedCollection(
    newCenter,
    newRadius,
    selectedLabels,
    selectedYear,
    selectedMonth
  );
  await getTwentyImages(queriedCollection);
  queryDB.updateHeatmapFromQuery(heatmap, queriedCollection);
}
async function getTwentyImages(
  queriedCollection: geofirestore.GeoQuery
): Promise<void> {
  const dataref = (await queriedCollection.get()).docs;
  const jump = Math.ceil(dataref.length / 10);
  const elementById = document.getElementById("images-holder");
  if (elementById != null) {
    elementById.innerHTML = "";
    for (let i = 0; i < dataref.length; i = i + jump) {
      const docData = dataref[i].data();
      const imageElement = document.createElement("img");
      imageElement.className = "sidepanel-image";
      imageElement.src = docData.url;
      elementById.appendChild(imageElement);
    }
  }
}

function queriesChanged(selectedQueries: {
  labels: string[];
  year: number | undefined;
  month: number | undefined;
}): void {
  selectedLabels = selectedQueries.labels;
  selectedYear = selectedQueries.year;
  selectedMonth = selectedQueries.month;
  mapChanged();
}

function toggleHeatmap() {
  heatmap.setMap(heatmap.getMap() ? null : map);
}

function changeGradient() {
  const gradient = [
    "rgba(0, 255, 255, 0)",
    "rgba(0, 255, 255, 1)",
    "rgba(0, 191, 255, 1)",
    "rgba(0, 127, 255, 1)",
    "rgba(0, 63, 255, 1)",
    "rgba(0, 0, 255, 1)",
    "rgba(0, 0, 223, 1)",
    "rgba(0, 0, 191, 1)",
    "rgba(0, 0, 159, 1)",
    "rgba(0, 0, 127, 1)",
    "rgba(63, 0, 91, 1)",
    "rgba(127, 0, 63, 1)",
    "rgba(191, 0, 31, 1)",
    "rgba(255, 0, 0, 1)",
  ];
  heatmap.set("gradient", heatmap.get("gradient") ? null : gradient);
}

function changeRadius() {
  heatmap.set("radius", heatmap.get("radius") ? null : 20);
}

function changeOpacity() {
  heatmap.set("opacity", heatmap.get("opacity") ? null : 0.2);
}

// [END maps_layer_heatmap]

export { initMap, database, queriesChanged };
