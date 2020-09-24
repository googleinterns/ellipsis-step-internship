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

/*@param docData The data of the image that is added to the sidepanel
  @param ElemntById The HTML element that will contain the new image  */
export function addImageToSidePanel(
  docData: firebase.firestore.DocumentData,
  elementById: HTMLElement
): HTMLImageElement {
  const imageElement = document.createElement("img");
  imageElement.className = "sidepanel-image";
  imageElement.src = docData.url;
  elementById.appendChild(imageElement);
  return imageElement;
}
