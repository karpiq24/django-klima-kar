import React from "react";
import PropTypes from "prop-types";
import Form from "react-bootstrap/Form";
import Alert from "react-bootstrap/Alert";

const DescriptionInput = ({ currentStep, onChange, commission, errors }) => {
    if (currentStep !== 6) return null;
    return (
        <>
            <div className="error-list">
                {errors.description
                    ? errors.description.map((error, idx) => (
                          <Alert key={idx} variant="danger">
                              {error}
                          </Alert>
                      ))
                    : null}
            </div>
            <Form.Group>
                <h2>Wprowadź opis zlecenia:</h2>
                <Form.Control
                    className="big-area"
                    as="textarea"
                    rows="4"
                    value={commission.description}
                    onChange={(e) => onChange({ description: e.target.value }, false)}
                />
            </Form.Group>
        </>
    );
};

DescriptionInput.propTypes = {
    currentStep: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
    commission: PropTypes.object.isRequired,
};

export default DescriptionInput;
