import React from "react";
import Sidebar from "react-sidebar";
import QueriesForm from "./components/queriesForm";
import ImagesHolder from "./components/imagesHolder";

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
      <Sidebar
        sidebar={
          <div>
            <button onClick={() => this.onSetSidebarOpen(false)}>
              Close sidebar
            </button>
            <QueriesForm data={this.props.labels} />
            <ImagesHolder
              id="images-sidepanel"
              data={[
                "https://live.staticflickr.com/3677/13545844805_170ec3746b_c.jpg",
                "https://live.staticflickr.com/3677/13545844805_170ec3746b_c.jpg",
              ]}
            />
          </div>
        }
        open={this.state.sidebarOpen}
        children={this.state.openButton}
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
          },
        }}
      />
    );
  }
}

export default SidePanel;
