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

import React from "react";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import Sidebar from "react-sidebar";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import QueriesForm from "./queriesForm";

/*Component that uses react-sidebar component. 
Contains all the features of the sidebar- the queries and the images.
The sidepanel can be open/closed according to a open/close button.*/
class SidePanel extends React.Component<
  { labels: Array<{ value: string; label: string }> },
  { sidebarOpen: boolean; openButton: JSX.Element | null }
> {
  constructor(props: { labels: Array<{ value: string; label: string }> }) {
    super(props);
    this.state = {
      sidebarOpen: true,
      openButton: null,
    };
    this.onSetSidebarOpen = this.onSetSidebarOpen.bind(this);
  }

  /*Changes sidebar states according to being open/close, if closed- need a "open sidebar" button. */
  onSetSidebarOpen(open: boolean): void {
    this.setState({ sidebarOpen: open });
    if (open) {
      //Does not show open sidebar button when open.
      this.setState({ openButton: null });
    } else {
      this.setState({
        openButton: (
          <button onClick={() => this.onSetSidebarOpen(true)}>
            Open sidebar
          </button>
        ),
      });
    }
  }

  render(): JSX.Element {
    return (
      <Sidebar
        sidebar={
          <div>
            <div id="fixed-sidebar">
              <button onClick={() => this.onSetSidebarOpen(false)}>
                Close sidebar
              </button>
              <QueriesForm data={this.props.labels} />
              <h4 id="num-of-results"></h4>
            </div>
            <div id="images-holder"></div>
          </div>
        }
        open={this.state.sidebarOpen}
        onSetOpen={this.onSetSidebarOpen}
        sidebarClassName="sidebarStyle"
        overlayClassName="overlayStyle"
        rootClassName="rootStyle"
      >
        <div>{this.state.openButton}</div>
      </Sidebar>
    );
  }
}

export default SidePanel;
