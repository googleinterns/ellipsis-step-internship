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
import * as firebase from 'firebase';
import firebaseConfig from './firebase_config';

// Creates the firebase app and gets a reference to firestore.
console.log(firebaseConfig);
var app = firebase.initializeApp(firebaseConfig);
var database = app.firestore();

 function initMap():void{


  map = new google.maps.Map(document.getElementById("map") as HTMLElement, {
    zoom: 13,
    mapTypeId: "satellite"
  });

  // TODO shows how to connect to firestore and read data from there
  let images = database.collection("test");
  images.get().then(querySnapshot => {
    if(!querySnapshot.empty) {
      
      const image = querySnapshot.docs[0].data() as any;
      console.log(image);
      map.setCenter(  { lat: image.coordinates.latitude, lng: image.coordinates.longitude });
      console.log(image);
    }
  });


  heatmap = new google.maps.visualization.HeatmapLayer({
    //data: getPointsByDate(1999),
    //data: queryAllDate(),
    data: getPointsByQeury(queryByDateAndLabel('dog',2000)),
    //data: getPoints(),
    map: map
  });
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
    "rgba(255, 0, 0, 1)"
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
export { initMap };



//*********************addind info into the DB: ************************** */


let coord=[
  [37.782551, -122.445368],[37.782745, -122.444586], [37.782842, -122.443688], [37.782919, -122.442815],[37.782992, -122.442112],[37.7831, -122.441461],
  [37.783206, -122.440829], [37.783273, -122.440324],[37.783316, -122.440023],[37.783357, -122.439794],[37.783371, -122.439687],
  [37.783368, -122.439666],[37.783383, -122.439594],[37.783508, -122.439525], [37.783842, -122.439591],[37.784147, -122.439668],
  [37.784206, -122.439686],[37.784386, -122.43979],[37.784701, -122.439902],[37.784965, -122.439938],[37.78501, -122.439947],[37.78536, -122.439952],[37.785715, -122.44003],
  [37.786117, -122.440119],[37.786564, -122.440209],[37.786905, -122.44027], [37.786956, -122.440279],[37.800224, -122.43352],[37.800155, -122.434101],[37.80016, -122.43443],[37.800378, -122.434527],
  [37.800738, -122.434598],[37.800938, -122.43465],[37.801024, -122.434889],[37.800955, -122.435392],[37.800886, -122.435959],
  [37.800811, -122.436275],[37.800788, -122.436299],[37.800719, -122.436302],[37.800702, -122.436298],[37.800661, -122.436273],[37.800395, -122.436172],
  [37.800228, -122.436116],[37.800169, -122.43613],[37.800066, -122.436167],[37.784345, -122.422922],
  [37.784389, -122.422926], [37.784437, -122.422924], [37.784746, -122.422818],[37.785436, -122.422959], [37.78612, -122.423112],
  [37.786433, -122.423029],[37.786631, -122.421213],[37.78666, -122.421033],[37.786801, -122.420141],[37.786823, -122.420034],
  [37.786831, -122.419916],[37.787034, -122.418208],[37.787056, -122.418034],[37.787169, -122.417145],[37.787217, -122.416715],
  [37.786144, -122.416403],[37.785292, -122.416257],[37.780666, -122.390374],[37.780501, -122.391281],[37.780148, -122.392052],
  [37.780173, -122.391148],[37.780693, -122.390592],[37.781261, -122.391142],[37.781808, -122.39173],[37.78234, -122.392341],
  [37.782812, -122.393022],[37.7833, -122.393672],[37.783809, -122.394275],[37.784246, -122.394979],[37.784791, -122.395958],[37.785675, -122.396746],
  [37.786262, -122.39578],[37.786776, -122.395093],[37.787282, -122.394426],[37.787783, -122.393767],[37.788343, -122.393184],[37.788895, -122.392506],[37.789371, -122.391701],[37.789722, -122.390952],[37.790315, -122.390305],[37.790738, -122.389616], [37.779448, -122.438702],[37.779023, -122.438585],[37.778542, -122.438492], [37.7781, -122.438411],[37.777986, -122.438376],[37.77768, -122.438313],[37.777316, -122.438273],[37.777135, -122.438254],
  [37.776987, -122.438303], [37.776946, -122.438404], [37.776944, -122.438467],[37.776892, -122.438459],[37.776842, -122.438442],[37.776822, -122.438391], [37.776814, -122.438412],
  [37.776787, -122.438628],[37.776729, -122.43865],[37.776759, -122.438677], [37.776772, -122.438498], [37.776787, -122.438389],
  [37.776848, -122.438283],[37.77687, -122.438239],[37.777015, -122.438198],[37.777333, -122.438256],[37.777595, -122.438308],[37.777797, -122.438344],[37.77816, -122.438442],
  [37.778414, -122.438508], [37.778445, -122.438516], [37.778503, -122.438529], [37.778607, -122.438549], [37.77867, -122.438644],[37.778847, -122.438706], [37.77924, -122.438744], [37.779738, -122.438822],
  [37.780201, -122.438882],[37.7804, -122.438905], [37.780501, -122.438921],[37.780892, -122.438986], [37.781446, -122.439087],
  [37.781985, -122.439199],[37.782239, -122.439249],[37.782286, -122.439266],[37.797847, -122.429388],[37.797874, -122.42918],[37.797885, -122.429069],[37.797887, -122.42905],
  [37.797933, -122.428954],[37.798242, -122.42899], [37.798617, -122.429075],[37.798719, -122.429092], [37.798944, -122.429145],
  [37.79932, -122.429251], [37.79959, -122.429309], [37.799677, -122.429324],[37.799966, -122.42936], [37.800288, -122.42943],
  [37.800443, -122.429461], [37.800465, -122.429474],[37.800644, -122.42954],[37.800948, -122.42962], [37.801242, -122.429685],[37.801375, -122.429702],[37.8014, -122.429703],[37.801453, -122.429707],[37.801473, -122.429709], [37.801532, -122.429707],
  [37.801852, -122.429729],[37.802173, -122.429789], [37.802459, -122.429847], [37.802554, -122.429825], [37.802647, -122.429549],
  [37.759977, -122.444591],[37.759913, -122.444698],[37.759623, -122.445065],[37.758902, -122.445158],[37.758428, -122.44457],[37.757687, -122.44334],[37.757583, -122.44324],
  [37.757019, -122.442787],[37.756603, -122.442322],[37.75638, -122.441602],[37.75579, -122.441382],[37.754493, -122.442133],[37.754361, -122.442206],[37.753719, -122.44265],[37.753096, -122.442915],[37.751617, -122.443211],[37.751496, -122.443246],[37.778824, -122.415092],
  [37.778833, -122.414932],[37.778834, -122.414898], [37.77874, -122.414757],[37.778501, -122.414433],[37.778182, -122.414026],
  [37.777851, -122.413623],[37.777486, -122.413166],[37.777109, -122.412674],[37.776743, -122.412186],[37.77644, -122.4118],[37.776295, -122.411614],[37.776158, -122.41144],[37.775806, -122.410997],[37.775422, -122.410484],
  [37.775126, -122.410087],[37.775012, -122.409854],[37.775164, -122.409573],[37.775498, -122.40918],[37.775868, -122.40873],
  [37.776256, -122.40824],[37.776519, -122.407928],[37.776539, -122.407904],[37.776595, -122.407854],[37.776853, -122.407547],[37.777234, -122.407087],
  [37.777644, -122.406558],[37.778066, -122.406017],[37.778468, -122.405499],[37.778866, -122.404995], [37.779295, -122.404455], [37.779695, -122.40395],[37.779982, -122.403584],[37.764826, -122.424922],
  [37.764796, -122.425375], [37.764782, -122.425869], [37.764768, -122.426089],[37.764766, -122.426117],
  [37.764723, -122.426276],[37.764681, -122.426649],[37.782012, -122.4042], [37.781574, -122.404911], [37.781055, -122.405597],
  [37.780479, -122.406341], [37.779996, -122.406939],[37.779459, -122.407613], [37.778953, -122.408228],[37.778409, -122.408839],[37.777842, -122.409501],
  [37.777334, -122.410181],[37.776809, -122.410836],[37.77624, -122.411514],[37.775725, -122.412145],[37.77519, -122.412805],[37.774672, -122.413464],[37.774084, -122.414186],
  [37.773533, -122.413636],[37.773021, -122.413009],[37.772501, -122.412371],[37.771964, -122.411681],[37.771479, -122.411078],[37.770992, -122.410477],[37.770467, -122.409801],
  [37.77009, -122.408904],[37.769657, -122.408103],[37.769132, -122.407276],[37.768564, -122.406469],[37.76798, -122.405745],[37.76738, -122.405299],[37.766604, -122.405297],[37.765838, -122.4052],
  [37.765139, -122.405139],[37.764457, -122.405094],[37.763716, -122.405142],[37.762932, -122.405398],[37.762126, -122.405813],[37.761344, -122.406215],
  [37.760556, -122.406495],[37.759732, -122.406484],[37.75891, -122.406228],[37.758182, -122.405695],[37.757676, -122.405118],[37.757039, -122.404346],
  [37.756335, -122.403719],[37.755503, -122.403406],[37.754665, -122.403242],[37.753837, -122.403172],[37.752986, -122.403112],[37.751266, -122.403355]] ;  

//addAllToDatabase();  //calls the function that adds all the data

//generate random date for the info in the DB
function randomDate()
{
  let day,month,year:number;
  day=Math.floor(Math.random() * 29) + 1;
  month=Math.floor(Math.random() * 12) + 1
  year=Math.floor(Math.random() * 30) + 1990
  return [day,month,year]
}

// add Single doc into DB
function addNewImage(label:string,lat: number, lng:number, year: number, month: number, day:number, url:string){
  let newDoc = database.collection('imagesTal').doc();
  newDoc.set({
    year: year,
    month: month, 
    day: day,
    url:url,
    label: [label],
    coordinates: new firebase.firestore.GeoPoint(lat, lng)  })
  newDoc.collection('labels').doc().set({
    name: label
  })
  }

//add random data into the DB with lon&lan and a random
function addAllToDatabase()
{
  let arraydate:number[];
  let randomnu: number;
  for (var _i = 0; _i < coord.length; _i++) {
    arraydate=randomDate()
    randomnu= Math.floor(Math.random() * 3)
    if (randomnu===0)
       addNewImage('dog',coord[_i][0], coord[_i][1],arraydate[2],arraydate[1],arraydate[0],'https://live.staticflickr.com/5284/5338762379_59f7435b93_c.jpg')
    if (randomnu===1)
      addNewImage('bag',coord[_i][0], coord[_i][1],arraydate[2],arraydate[1],arraydate[0],'https://live.staticflickr.com/65535/49748702651_07ae2b33b4_c.jpg')
    if (randomnu===2)
      addNewImage('cat',coord[_i][0], coord[_i][1],arraydate[2],arraydate[1],arraydate[0],'https://live.staticflickr.com/3677/13545844805_170ec3746b_c.jpg')
  }
}



//******************************qeuring the database********************************************** */


//a function than returns all the coordinates
function queryAllData():Array<google.maps.LatLng>
{
  let allpoints : Array<google.maps.LatLng> = [];
  let images = database.collection("imagesTal");
  images.get().then(
     queryImages => { queryImages.forEach(
        doc=> {prinInfoOnObject(doc);
          allpoints.push( nowlatlon( doc.get('coordinates').latitude, doc.get('coordinates').longitude ))})});
    return allpoints  
}

//a function than returns all the coordinates in a certain year
function qeuryByYear(year_:number)
{
  let allpoints : Array<google.maps.LatLng> = []; 
  let dataRef:firebase.firestore.Query = database.collection('imagesTal');
  return dataRef.where('year', '==', year_);
} 

//a function returns a fillter collection that contain coordinates in a certain time from a certain label
function queryByDateAndLabel(_label:string,_year?: number, _month?: number, _day?:number)
{
  let allpoints : Array<google.maps.LatLng> = []; 
  let dataRef:firebase.firestore.Query = database.collection('imagesTal');
  dataRef = dataRef.where('label', 'array-contains', _label);
  if (_year != undefined)
    dataRef = dataRef.where('year', '==', _year);
  if (_year != undefined && _month!=undefined)
    dataRef = dataRef.where('month', '==', _month)
  if (_year != undefined && _month!=undefined && _day!=undefined)
    dataRef = dataRef.where('day', '==', _day);
  return dataRef;
}

//this function recives a filterd colection and returns all the geo points
function getPointsByQeury(dataRef :firebase.firestore.Query)
{
  let allpoints : Array<google.maps.LatLng> = []; 
  dataRef.get().then(
    queryImages => { queryImages.forEach(
       doc=> {prinInfoOnObject(doc);
         allpoints.push( nowlatlon( doc.get('coordinates').latitude, doc.get('coordinates').longitude ))})});
   return allpoints 
}

//creats new geo point
function nowlatlon(lat:number,lon:number):google.maps.LatLng
{
  return new google.maps.LatLng(lat, lon);
}

//prints out info on the object in the data base hlps for debuging
function prinInfoOnObject(doc:firebase.firestore.QueryDocumentSnapshot<firebase.firestore.DocumentData>)
{
  console.log(doc.get('label'));
  console.log(doc.get('year'));
  console.log(doc.get('month'));
  console.log(doc.get('day'));
  console.log(doc.get('coordinates'));
}





