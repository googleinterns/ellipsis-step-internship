/*
 * Copyright 2019 Google LLC. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
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
import * as firebase from "firebase";
import firebaseConfig from "./firebase_config";
import * as geofirestore from "geofirestore";

// Creates the firebase app and gets a reference to firestore.
console.log(firebaseConfig);
const app = firebase.initializeApp(firebaseConfig);
const database = app.firestore();

function initMap(): void {
  map = new google.maps.Map(document.getElementById("map") as HTMLElement, {
    zoom: 13,
    mapTypeId: "satellite",
  });

  // TODO shows how to connect to firestore and read data from there
  const images = database.collection("test");
  images.get().then((querySnapshot) => {
    if (!querySnapshot.empty) {
      const image = querySnapshot.docs[0].data() as any;
      console.log(image);
      map.setCenter({
        lat: image.coordinates.latitude,
        lng: image.coordinates.longitude,
      });
      console.log(image);
    }
  });

  heatmap = new google.maps.visualization.HeatmapLayer({
    //data: getPointsByDate(1999),
    //data: queryAllDate(),
    //data: getPointsByQeury(queryByDateAndLabel('dog',2000)),
    //data: getPoints(),
    data: [],
    map: map,
  });
  //getPointsByQeury(heatmap, queryByDateAndLabel("dog", 2000));
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

// Heatmap data: 500 Points
function getPoints() {
  // Create a reference to the cities collection
  //TODO update this to query firestore for image coordinates.
  return [
    new google.maps.LatLng(37.784345, -122.422922),
    new google.maps.LatLng(37.784389, -122.422926),
    new google.maps.LatLng(37.784437, -122.422924),
    new google.maps.LatLng(37.784746, -122.422818),
    new google.maps.LatLng(37.785436, -122.422959),
    new google.maps.LatLng(37.78612, -122.423112),
    new google.maps.LatLng(37.786433, -122.423029),
    new google.maps.LatLng(37.786631, -122.421213),
    new google.maps.LatLng(37.786905, -122.44027),
    new google.maps.LatLng(37.786956, -122.440279),
    new google.maps.LatLng(37.800224, -122.43352),
    new google.maps.LatLng(37.800155, -122.434101),
    new google.maps.LatLng(37.80016, -122.43443),
    new google.maps.LatLng(37.800378, -122.434527),
    new google.maps.LatLng(37.800738, -122.434598),
    new google.maps.LatLng(37.800938, -122.43465),
    new google.maps.LatLng(37.801024, -122.434889),
    new google.maps.LatLng(37.800955, -122.435392),
    new google.maps.LatLng(37.800886, -122.435959),
  ];
}

// [END maps_layer_heatmap]

function add(value1: number, value2: number) {
  return value1 + value2;
}

export { initMap, add };
