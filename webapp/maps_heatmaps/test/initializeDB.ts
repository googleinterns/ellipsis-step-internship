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

import { database } from "../src/declareDatabase";
import * as firebase from "firebase";
import { DateTime } from "../src/interface";
import fs from "fs";
import * as geokit from "geokit";

initializeDB();

/* Reads from a given file and stores in the database. */
function initializeDB() {
  const allCoordinates: number[][] = new Array<Array<number>>();
  if (process.argv.length < 3) {
    console.log("ERROR: not in format - npm run initialize-db fileName.txt");
  } else {
    const filename = process.argv[2];
    fs.readFile(filename, "utf8", function (err, data) {
      if (err) {
        console.log(err);
      } else {
        const textByLine = data.toString().split("\n");
        textByLine.forEach((element) => {
          const inerArray = element.toString().split(",");
          const lat: number = +inerArray[0];
          const lng: number = +inerArray[1];
          const coord: number[] = [lat, lng];
          allCoordinates.push(coord);
        });
      }
      addImagesToDB(allCoordinates);
    });
  }
}

/* @param url The source of the image
  @param label The label found in the image
  @param lat, lng The coordinates of the image
  @param year, month, day The date the image was taken
Adds an image to 'images' collection.*/
//TODO: add subcollection of labels to each image.
function addNewImage(
  url: string,
  label: string,
  lat: number,
  lng: number,
  date: DateTime,
  attribution: string,
  random: number
) {
  //const GeoFirestore = geofirestore.initializeApp(database);
  //const geocollection = GeoFirestore.collection("imagesTal");

  database.collection("Images").add({
    date: date,
    coordinates: new firebase.firestore.GeoPoint(lat, lng),
    hashmap: {
      hash1: geokit.hash({ lat: lat, lng: lng }, 1),
      hash2: geokit.hash({ lat: lat, lng: lng }, 2),
      hash3: geokit.hash({ lat: lat, lng: lng }, 3),
      hash4: geokit.hash({ lat: lat, lng: lng }, 4),
      hash5: geokit.hash({ lat: lat, lng: lng }, 5),
      hash6: geokit.hash({ lat: lat, lng: lng }, 6),
      hash7: geokit.hash({ lat: lat, lng: lng }, 7),
      hash8: geokit.hash({ lat: lat, lng: lng }, 8),
      hash9: geokit.hash({ lat: lat, lng: lng }, 9),
      hash10: geokit.hash({ lat: lat, lng: lng }, 10),
    },
    labels: [label],
    url: url,
    attribution: attribution,
    random: random,
  });
}

/* Adds images to 'images' collection with randomized information
from a set of coordinates.*/
function addImagesToDB(points: Array<Array<number>>): void {
  points.forEach((element) => {
    const latitude = element[0];
    const longitude = element[1];
    const date = {
      year: 1990 + getRandomNumber(31),
      month: getRandomNumber(12) + 1,
      day: getRandomNumber(30) + 1,
    };
    const numOfLabel = getRandomNumber(3);
    const label = ["dog", "bag", "cat"][numOfLabel];
    const url = [
      "https://live.staticflickr.com/5284/5338762379_59f7435b93_c.jpg",
      "https://live.staticflickr.com/65535/49748702651_07ae2b33b4_c.jpg",
      "https://live.staticflickr.com/3677/13545844805_170ec3746b_c.jpg",
    ][numOfLabel];
    const attribution = ["Tal", "Ofri", "Anonymus"][numOfLabel];
    const random = getRandomNumber(100);
    addNewImage(url, label, latitude, longitude, date, attribution, random);
  });
}

/* Returns a random integer from 0 to max-1. */
function getRandomNumber(max: number) {
  return Math.floor(Math.random() * Math.floor(max));
}

export { addImagesToDB };
