import {database, heatmap} from './index';
import * as firebase from 'firebase';


/* returns the filtered collection by the different queries*/
function getQuiredCollection(labels: string[], year?: number, month?: number, day?: number): firebase.firestore.Query {
    let dataRef: firebase.firestore.Query = 
    database.collection('images').where('labels', 'array-contains-any', labels);
    if (year != undefined)
      dataRef = dataRef.where('year', '==', year);	    
    if (year != undefined && month!=undefined)	  
      dataRef = dataRef.where('month', '==', month);
    if (year != undefined && month!=undefined && day!=undefined)	 
      dataRef = dataRef.where('day', '==', day);
    return dataRef;
    }

/* displays the relevant images on the map
 given the filtered collection and the heapmap*/
function getPointsFromDB(heatmap : google.maps.visualization.HeatmapLayer, dataRef: firebase.firestore.Query){
    const allpoints : Array<google.maps.LatLng> = [];
   dataRef.get()
    .then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
          let coordinates : firebase.firestore.GeoPoint = doc.get('coordinates')
          let newLatLon = getLatLon(coordinates);
          allpoints.push(newLatLon);
      });
      heatmap.setData(allpoints); 
  });
  }
  
  function getLatLon(coordinates: firebase.firestore.GeoPoint){
    const lat = coordinates.latitude;
    const lng = coordinates.longitude;
    return new google.maps.LatLng(lat, lng);
  }

 export { getPointsFromDB, getQuiredCollection}
  