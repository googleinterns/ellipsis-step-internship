import { database } from "../src/index";
import * as firebase from "firebase";
import * as geofirestore from "geofirestore";
import fs from "fs";

/**
 * initalize the database
 * to run in the terminal-  npm run initialize-db
 */

/* Reads from a given file and converts to an array of coordinates. */
function getCoordinatesFromFile() {
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
          const lon: number = +inerArray[1];
          const coord: number[] = [lat, lon];
          allCoordinates.push(coord);
        });
      }
      return allCoordinates;
    });
  }
}

//addImagesToDB(getCoordinatesFromFile());

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

export { addImagesToDB };
