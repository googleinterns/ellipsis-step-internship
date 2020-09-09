import React from "react";

class ImagesHolder extends React.Component<
  { id: string; data: Array<string> },
  any
> {
  render(): JSX.Element {
    const images: JSX.Element[] = [];
    this.props.data.forEach((url: string) => {
      images.push(<img className="sidepanel-image" src={url} />);
    });
    return <div>{images}</div>;
  }
}

export default ImagesHolder;
