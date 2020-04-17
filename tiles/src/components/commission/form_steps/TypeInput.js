import React from "react";
import PropTypes from "prop-types";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";

const TypeInput = ({ currentStep, commission, onChange }) => {
    if (currentStep !== 1) return null;
    return (
        <Form.Group>
            <h2>Zlecenie dotyczy:</h2>
            <div className="type-buttons">
                <Button
                    type="button"
                    variant="outline-primary"
                    active={commission.commission_type === "VH"}
                    size="xxl"
                    onClick={() => {
                        if(commission.commission_type === "CO") {
                            onChange({ commission_type: "VH", component: null, vc_name: null }, true);
                        } else {
                            onChange({commission_type: "VH", component: null}, true);
                        }
                    }}
                >
                    POJAZDU
                </Button>
                <p>czy</p>
                <Button
                    type="button"
                    variant="outline-primary"
                    active={commission.commission_type === "CO"}
                    size="xxl"
                    onClick={() => {
                        if(commission.commission_type === "VH") {
                            onChange({ commission_type: "CO", vehicle: null, vc_name: null }, true);
                        } else {
                            onChange({commission_type: "CO", vehicle: null}, true);
                        }
                    }}
                >
                    PODZESPOŁU
                </Button>
            </div>
        </Form.Group>
    );
};

TypeInput.propTypes = {
    currentStep: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
};

export default TypeInput;
