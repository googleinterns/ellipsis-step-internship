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

  onYearChange = (selectedOption: any): void => {
    this.setState({ year: selectedOption.value }, () => {
      queriesChanged(this.state);
    });
  };
  onMonthChange = (selectedOption: any): void => {
    this.setState({ month: selectedOption.value }, () => {
      queriesChanged(this.state);
    });
    queriesChanged(this.state);
  };
  onLabelChange = (selectedOption: any): void => {
    if (selectedOption && selectedOption.length > 0) {
      this.setState(
        {
          labels: selectedOption.map((x: Record<string, string>) => x.label),
        },
        () => {
          queriesChanged(this.state);
        }
      );
    } else {
      this.setState(
        {
          labels: this.props.data.map((x: Record<string, string>) => x.label),
        },
        () => {
          queriesChanged(this.state);
        }
      );
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
