import React from "react";
import Select from "react-select";

class QueriesForm extends React.Component<
  { labels: Array<Record<string, string>> },
  {
    selectedLabels: string[] | null; //TODO: make default labels or not allow to submit without choosing at leat one label.
    year: number | undefined;
    month: number | undefined;
  }
> {
  constructor(props: { labels: Array<Record<string, string>> }) {
    super(props);
    this.state = {
      selectedLabels: null,
      year: undefined,
      month: undefined,
    };
  }

  onSubmit = (): void => {
    alert(
      "submitted " +
        this.state.year +
        " " +
        this.state.month +
        " " +
        this.state.selectedLabels
    );
  };

  onYearChange = (event: any): void => {
    this.setState({ year: event.target.value });
  };
  onMonthChange = (event: any): void => {
    this.setState({ month: event.target.value });
  };

  onLabelChange = (selectedOption: any): void => {
    this.setState({
      selectedLabels: selectedOption.map(
        (x: Record<string, string>) => x.value
      ),
    });
  };

  render(): JSX.Element {
    return (
      <form className="queriesForm" onSubmit={this.onSubmit}>
        <div className="formRow">
          <label>Labels:</label>
          <Select
            isSearchable={true}
            isMulti={true}
            options={this.props.labels}
            onChange={this.onLabelChange}
          />
        </div>
        <div className="formRow">
          <label>Year:</label>
          <input
            type="number"
            id="year"
            min="1990"
            max="2020"
            onChange={this.onYearChange}
          />
        </div>

        <div className="formRow">
          <label>Month:</label>
          <input
            type="number"
            id="month"
            min="1"
            max="12"
            onChange={this.onMonthChange}
          />
        </div>
        <input type="submit" value="Submit" />
      </form>
    );
  }
}

export default QueriesForm;
