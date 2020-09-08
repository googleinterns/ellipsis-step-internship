import React from "react";
import Sidebar from "react-sidebar";
import QueriesForm from "./components/queriesForm";

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
      <div>
        <Sidebar
          sidebar={
            <div>
              <QueriesForm labels={this.props.labels} />
              <button onClick={() => this.onSetSidebarOpen(false)}>
                Close sidebar
              </button>
            </div>
          }
          open={this.state.sidebarOpen}
          onSetOpen={this.onSetSidebarOpen}
          styles={{
            sidebar: {
              backgroundColor: "rgba(255, 255, 255, 0.9)",
              width: "250px",
              zIndex: "5",
            },
          }}
        >
          {this.state.openButton}
        </Sidebar>
      </div>
    );
  }
}

export default SidePanel;
