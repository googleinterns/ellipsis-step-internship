import * as queryDB from "./queryDB";
import { database } from "./index";
import { expect } from "chai";
import "mocha";
import firebase from "firebase";
import * as geofirestore from "geofirestore";

/*
describe("add new lat lon", () => {
  it("correctly creating new lat lon", () => {
    const lat = 37;
    const lon = -120;
    const coordinates: firebase.firestore.GeoPoint = new firebase.firestore.GeoPoint(
      lat,
      lon
    );
    const result = queryDB.getLatLon(coordinates);
    expect(result).to.equal(new google.maps.LatLng(lat, lon));
  });
});
*/

describe("get coordinates by qeury", () => {
  it("get by all arguments", () => {
    const lat = 37.780501;
    const lon = -122.391281;
    const center = new firebase.firestore.GeoPoint(lat, lon);
    const radius = 100;
    const year = 2015;
    const month = 4;
    const day = 20;
    const label = ["cat"];
    const result: geofirestore.GeoQuery = queryDB.getQuiredCollection(
      center,
      radius,
      label,
      year,
      month,
      day
    );
    const GeoFirestore = geofirestore.initializeApp(database);
    const geoCollection = GeoFirestore.collection("images");
    const wontedOutput: geofirestore.GeoQuery = geoCollection
      .near({
        center: center,
        radius: radius,
      })
      .where("labels", "array-contains-any", label)
      .where("year", "==", year)
      .where("month", "==", month)
      .where("day", "==", day);
    expect(result).to.equal(wontedOutput);
  });
});

describe("get coordinates by qeury1", () => {
  it("get by all arguments1", () => {
    const lat = 37.780501;
    const lon = -122.391281;
    const center = new firebase.firestore.GeoPoint(lat, lon);
    const radius = 100;
    const year = 2015;
    const month = 4;
    const day = 20;
    const label = ["cat"];
    const result: geofirestore.GeoQuery = queryDB.getQuiredCollection(
      center,
      radius,
      label,
      year,
      month,
      day
    );
    const GeoFirestore = geofirestore.initializeApp(database);
    const geoCollection = GeoFirestore.collection("images");
    const wontedOutput: geofirestore.GeoQuery = geoCollection
      .near({
        center: center,
        radius: radius,
      })
      .where("labels", "array-contains-any", label)
      .where("year", "==", year)
      .where("month", "==", month)
      .where("day", "==", day);
    expect(result).to.equal(wontedOutput);
  });
});
