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

import { database } from "./declareDatabase";

const LABELS_MAP: Promise<Map<any, any>> = createLabelMap();

/* Queries the database for the LabelTags collection and creates
a map containing the key as the label id and the value as the label name*/
async function createLabelMap(): Promise<Map<any, any>> {
  const labelMap = new Map();
  const docs = (await database.collection("LabelTags").get()).docs;
  for (let i = 0; i < docs.length; i++) {
    const doc = docs[i];
    const id = doc.id;
    const label = doc.data().name;
    labelMap.set(id, label);
  }
  return labelMap;
}

/* This function converts from an array containing label ides 
to an array containing the corresponding label names.*/
export async function convertLabelIdToLabelName(
  idArray: Array<string>
): Promise<string[]> {
  const labelMap: Map<any, any> = await LABELS_MAP;
  const labelArray: Array<string> = [];
  idArray.forEach((id) => labelArray.push(labelMap.get(id)));
  return labelArray;
}
