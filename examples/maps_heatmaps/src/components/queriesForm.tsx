import React from "react";
import Select from "react-select";
import { queriesChanged } from "../index";

class QueriesForm extends React.Component<
  { data: Array<Record<string, string>> },
  {
    labels: string[];
    year: number | undefined;
    month: number | undefined;
  }
> {
  constructor(props: { data: Array<Record<string, string>> }) {
    super(props);
    this.state = {
      labels: this.props.data.map((x: Record<string, string>) => x.label),
      year: undefined,
      month: undefined,
    };
  }

  onSubmit = (event: any): void => {
    event.preventDefault();
    console.log(this.state.labels);
    if (this.state.labels.length == 0) {
      //TODO: verify that if labels were not chosen, it will show all labels.
      alert("Select labels before submitting");
    }
    queriesChanged(this.state);
  };

  onYearChange = (selectedOption: any): void => {
    this.setState({ year: selectedOption.value });
  };
  onMonthChange = (selectedOption: any): void => {
    this.setState({ month: selectedOption.value });
  };
  onLabelChange = (selectedOption: any): void => {
    if (selectedOption) {
      this.setState({
        labels: selectedOption.map((x: Record<string, string>) => x.label),
      });
    }
  };
  getYears() {
    const years: Array<Record<string, number | undefined | string>> = [
      { value: undefined, label: "Select all" },
    ];
    for (let i = 1990; i <= 2020; i++) {
      years.push({ value: i, label: i });
    }
    return years;
  }
  getMonths() {
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
      <form className="queriesForm" onSubmit={this.onSubmit}>
        <div className="formRow">
          <label>Labels:</label>
          <Select
            isSearchable={true}
            isMulti={true}
            options={this.props.data}
            onChange={this.onLabelChange}
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
            isSearchable={true}
            options={this.getMonths()}
            onChange={this.onMonthChange}
          />
        </div>
        <input id="submit" type="submit" value="Submit" />
      </form>
    );
  }
}

export default QueriesForm;
