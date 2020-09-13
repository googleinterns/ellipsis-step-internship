import React from "react";
import Sidebar from "react-sidebar";
import QueriesForm from "./queriesForm";

class SidePanel extends React.Component<
  { labels: Array<Record<string, string>> },
  { sidebarOpen: boolean; openButton: JSX.Element | null }
> {
  constructor(props: any) {
    super(props);
    this.state = {
      sidebarOpen: true,
      openButton: null,
    };
    this.onSetSidebarOpen = this.onSetSidebarOpen.bind(this);
  }

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
            </div>
            <div id="images-holder"></div>
          </div>
        }
        open={this.state.sidebarOpen}
        onSetOpen={this.onSetSidebarOpen}
        styles={{
          overlay: {
            width: "255px",
          },
          root: {
            width: "255px",
          },
          sidebar: {
            backgroundColor: "rgba(255, 255, 255, 0.9)",
            width: "255px",
            zIndex: "5",
            position: "fixed",
          },
        }}
      >
        <div>{this.state.openButton}</div>
      </Sidebar>
    );
  }
}

export default SidePanel;
