import React from "react";
import PropTypes from "prop-types";
import ToggleButtonGroup from "react-bootstrap/ToggleButtonGroup";
import ToggleButton from "react-bootstrap/ToggleButton";
import Form from "react-bootstrap/Form";
import { CANCELLED, DONE, ON_HOLD, OPEN, READY } from "../choices";
import Alert from "react-bootstrap/Alert";

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
                <div className="commission-status-buttons">
                    <ToggleButtonGroup type="radio" name="type" className="pretty-select" value={commission.status}>
                        <ToggleButton
                            value={OPEN}
                            variant="outline-primary"
                            size="xxl"
                            active
                            onClick={() => onChange({ status: OPEN, end_date: null }, true)}
                        >
                            OTWARTE
                        </ToggleButton>
                        <ToggleButton
                            value={READY}
                            variant="outline-primary"
                            size="xxl"
                            onClick={() => onChange({ status: READY, end_date: null }, true)}
                        >
                            GOTOWE
                        </ToggleButton>
                        <ToggleButton
                            value={DONE}
                            variant="outline-primary"
                            size="xxl"
                            onClick={() => {
                                if (commission.end_date === null) {
                                    onChange({ status: DONE, end_date: new Date() }, true);
                                } else {
                                    onChange({ status: DONE }, true);
                                }
                            }}
                        >
                            ZAMKNIĘTE
                        </ToggleButton>
                        <ToggleButton
                            value={ON_HOLD}
                            variant="outline-primary"
                            size="xxl"
                            onClick={() => onChange({ status: ON_HOLD, end_date: null }, true)}
                        >
                            WSTRZYMANE
                        </ToggleButton>
                        <ToggleButton
                            value={CANCELLED}
                            variant="outline-primary"
                            size="xxl"
                            onClick={() => {
                                if (commission.end_date === null) {
                                    onChange({ status: CANCELLED, end_date: new Date() }, true);
                                } else {
                                    onChange({ status: CANCELLED }, true);
                                }
                            }}
                        >
                            ANULOWANE
                        </ToggleButton>
                    </ToggleButtonGroup>
                </div>
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
