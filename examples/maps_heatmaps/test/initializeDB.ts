import { database } from "../src/index";
import * as firebase from "firebase";
import * as geofirestore from "geofirestore";
import fs from "fs";

/**
 * initalize the database
 * to run in the terminal-  npm run initialize-db
 */

const allCoordinates = [];
fs.readFile("./coordinates.txt", function (text) {
  const textByLine = text.split("\n");
});

addImagesToDB(allCoordinates);

/* adds an image to 'images' collection*/
function addNewImage(
  url: string,
  label: string,
  lat: number,
  lng: number,
  year: number,
  month: number,
  day: number
) {
  const GeoFirestore = geofirestore.initializeApp(database);
  const geocollection = GeoFirestore.collection("images");
  const newDoc = geocollection.add({
    year: year,
    month: month,
    day: day,
    coordinates: new firebase.firestore.GeoPoint(lat, lng),
    labels: [label],
    url: url,
  });
  // newDoc.collection("labels").doc().set({
  //   name: label,
  // });
}

/* adds images to 'images' collection with randomized information
 from a set of coordinates*/
function addImagesToDB(points: Array<Array<number>>) {
  points.forEach((element) => {
    const latitude = element[0];
    const longitude = element[1];
    const year = 1990 + getRandomNumber(31);
    const month = getRandomNumber(12) + 1;
    const day = getRandomNumber(30) + 1;
    const numOfLabel = getRandomNumber(3);
    const label = ["dog", "bag", "cat"][numOfLabel];
    const url = [
      "https://live.staticflickr.com/5284/5338762379_59f7435b93_c.jpg",
      "https://live.staticflickr.com/65535/49748702651_07ae2b33b4_c.jpg",
      "https://live.staticflickr.com/3677/13545844805_170ec3746b_c.jpg",
    ][numOfLabel];
    addNewImage(url, label, latitude, longitude, year, month, day);
  });
}

/* returns a random integer from 0 to max-1*/
function getRandomNumber(max: number) {
  return Math.floor(Math.random() * Math.floor(max));
}

export { addImagesToDB, allCoordinates };
