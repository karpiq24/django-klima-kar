import React from "react";
import Spinner from "react-bootstrap/Spinner";

const ContentLoading = props => {
    return (
        <div className="content-loading">
            <Spinner animation="border" variant="primary" />
        </div>
    );
};

export default ContentLoading;
