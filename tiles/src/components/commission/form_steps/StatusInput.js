import React from "react";
import PropTypes from "prop-types";
import Form from "react-bootstrap/Form";
import Alert from "react-bootstrap/Alert";
import StatusButtons from "./StatusButtons";

const StatusInput = ({ currentStep, onChange, commission, errors }) => {
    if (currentStep !== 4) return null;
    return (
        <>
            <div className="error-list">
                {errors.status
                    ? errors.status.map((error, idx) => (
                          <Alert key={idx} variant="danger">
                              {error}
                          </Alert>
                      ))
                    : null}
            </div>
            <Form.Group>
                <h2>Wybierz status zlecenia:</h2>
                <StatusButtons commission={commission} onChange={onChange} />
            </Form.Group>
        </>
    );
};

StatusInput.propTypes = {
    currentStep: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
    commission: PropTypes.object.isRequired,
};

export default StatusInput;
