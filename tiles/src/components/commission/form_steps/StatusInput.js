import React from "react";
import PropTypes from "prop-types";
import ToggleButtonGroup from "react-bootstrap/ToggleButtonGroup";
import ToggleButton from "react-bootstrap/ToggleButton";
import Form from "react-bootstrap/Form";

const StatusInput = ({ currentStep, onChange, commission }) => {
    if (currentStep !== 4) return null;
    return (
        <Form.Group>
            <h2>Wybierz status zlecenia:</h2>
            <div className="commission-status-buttons">
                <ToggleButtonGroup type="radio" name="type" className="pretty-select" value={commission.status}>
                    <ToggleButton
                        value={"OP"}
                        variant="outline-primary"
                        size="xxl"
                        active
                        onClick={() => onChange({ status: "OP", end_date: null }, true)}
                    >
                        OTWARTE
                    </ToggleButton>
                    <ToggleButton
                        value={"RE"}
                        variant="outline-primary"
                        size="xxl"
                        onClick={() => onChange({ status: "RE", end_date: null }, true)}
                    >
                        GOTOWE
                    </ToggleButton>
                    <ToggleButton
                        value={"DO"}
                        variant="outline-primary"
                        size="xxl"
                        onClick={() => {
                            if (commission.end_date === null) {
                                onChange({ status: "DO", end_date: new Date() }, true);
                            }
                            else {
                                onChange({ status: "DO" }, true);
                            }
                        }}
                    >
                        ZAMKNIĘTE
                    </ToggleButton>
                    <ToggleButton
                        value={"HO"}
                        variant="outline-primary"
                        size="xxl"
                        onClick={() => onChange({ status: "HO", end_date: null }, true)}
                    >
                        WSTRZYMANE
                    </ToggleButton>
                    <ToggleButton
                        value={"CANCELLED"}
                        variant="outline-primary"
                        size="xxl"
                        onClick={() => {
                            if (commission.end_date === null) {
                                onChange({ status: "CA", end_date: new Date() }, true);
                            }
                            else {
                                onChange({ status: "CA" }, true);
                            }
                        }}
                    >
                        ANULOWANE
                    </ToggleButton>
                </ToggleButtonGroup>
            </div>
        </Form.Group>
    );
};

StatusInput.propTypes = {
    currentStep: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
    commission: PropTypes.object.isRequired,
};

export default StatusInput;
