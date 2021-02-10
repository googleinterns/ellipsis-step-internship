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
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/explicit-module-boundary-types */

import React from "react";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import Select from "react-select";
import { queriesChanged } from "../index";

/*Component that holds and controls the label, year and month queries.
The component uses react-select component for each query,
and it updates the map with any change. */
class QueriesForm extends React.Component<
  { data: Array<{ value: string; label: string }> },
  {
    labels: string[];
    year: number | undefined;
    month: number | undefined;
  }
> {
  constructor(props: { data: Array<{ value: string; label: string }> }) {
    super(props);
    this.state = {
      labels: this.props.data.map((x: Record<string, string>) => x.value),
      year: undefined,
      month: undefined,
    };
  }
  onLabelChange = (selectedOption: any): void => {
    //At least one label was chosen.
    if (selectedOption && selectedOption.length > 0) {
      this.setState(
        {
          labels: selectedOption.map((x: Record<string, string>) => x.value),
        },
        () => {
          queriesChanged(this.state);
        }
      );
      //No labels chosen. Show all labels.
    } else {
      this.setState(
        {
          labels: this.props.data.map((x: Record<string, string>) => x.value),
        },
        () => {
          queriesChanged(this.state);
        }
      );
    }
  };
  disableMonth = true; //Created to enable/disable month query according to year.

  onYearChange = (selectedOption: any): void => {
    this.setState({ year: selectedOption.value }, () => {
      queriesChanged(this.state);
    });
    //Enable choosing month only if year is chosen.
    //TODO: Change month-field to default when disabled.
    if (selectedOption.value != undefined) {
      this.disableMonth = false;
    } else {
      this.disableMonth = true;
    }
  };
  onMonthChange = (selectedOption: any): void => {
    this.setState({ month: selectedOption.value }, () => {
      queriesChanged(this.state);
    });
  };

  /*Creates year-options for select.*/
  //TODO: add dynamic years from database.
  getYears(): Array<Record<string, number | undefined | string>> {
    const years: Array<Record<string, number | undefined | string>> = [
      { value: undefined, label: "Select all" },
    ];
    for (let i = 2021; i >= 1990; i--) {
      years.push({ value: i, label: i });
    }
    return years;
  }
  /*Creates month-options for select.*/
  getMonths(): Array<Record<string, number | undefined | string>> {
    const months: Array<Record<string, number | undefined | string>> = [
      { value: undefined, label: "Select all" },
    ];
    for (let i = 1; i <= 12; i++) {
      months.push({ value: i, label: i });
    }
    return months;
  }

  render(): JSX.Element {
    return (
      <form className="queriesForm">
        <div className="formRow">
          <label>Labels:</label>
          <Select
            isSearchable={true}
            isMulti={true}
            options={this.props.data}
            onChange={(e) => this.onLabelChange(e)}
          />
        </div>
        <div className="formRow">
          <label>Year:</label>
          <Select
            isSearchable={true}
            options={this.getYears()}
            onChange={this.onYearChange}
          />
        </div>

        <div className="formRow">
          <label>Month:</label>
          <Select
            isDisabled={this.disableMonth}
            isSearchable={true}
            options={this.getMonths()}
            onChange={this.onMonthChange}
          />
        </div>
      </form>
    );
  }
}

export default QueriesForm;
