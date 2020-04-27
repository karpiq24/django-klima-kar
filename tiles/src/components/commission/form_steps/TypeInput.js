import React from "react";
import PropTypes from "prop-types";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { COMPONENT, VEHICLE } from "../choices";
import Alert from "react-bootstrap/Alert";

const TypeInput = ({ currentStep, commission, onChange, errors }) => {
    if (currentStep !== 1) return null;
    return (
        <>
            <div className="error-list">
                {errors.commission_type
                    ? errors.commission_type.map((error, idx) => (
                          <Alert key={idx} variant="danger">
                              {error}
                          </Alert>
                      ))
                    : null}
            </div>
            <Form.Group>
                <h2>Zlecenie dotyczy:</h2>
                <div className="type-buttons">
                    <Button
                        type="button"
                        variant="outline-primary"
                        active={commission.commission_type === VEHICLE}
                        size="xxl"
                        onClick={() => {
                            if (commission.commission_type === COMPONENT) {
                                onChange({ commission_type: VEHICLE, component: null, vc_name: null }, true);
                            } else {
                                onChange({ commission_type: VEHICLE, component: null }, true);
                            }
                        }}
                    >
                        POJAZDU
                    </Button>
                    <p>czy</p>
                    <Button
                        type="button"
                        variant="outline-primary"
                        active={commission.commission_type === COMPONENT}
                        size="xxl"
                        onClick={() => {
                            if (commission.commission_type === VEHICLE) {
                                onChange({ commission_type: COMPONENT, vehicle: null, vc_name: null }, true);
                            } else {
                                onChange({ commission_type: COMPONENT, vehicle: null }, true);
                            }
                        }}
                    >
                        PODZESPOŁU
                    </Button>
                </div>
            </Form.Group>
        </>
    );
};

TypeInput.propTypes = {
    currentStep: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
};

export default TypeInput;
