import React from "react";
import PropTypes from "prop-types";
import ToggleButtonGroup from "react-bootstrap/ToggleButtonGroup";
import ToggleButton from "react-bootstrap/ToggleButton";
import { CANCELLED, DONE, ON_HOLD, OPEN, READY } from "../choices";

const StatusButtons = ({ onChange, commission, size }) => {
    return (
        <div className="commission-status-buttons">
            <ToggleButtonGroup type="radio" name="type" className="pretty-select" value={commission.status}>
                <ToggleButton
                    value={OPEN}
                    variant="outline-primary"
                    size={size || "xxl"}
                    active
                    onClick={() => onChange({ status: OPEN, end_date: null }, true)}
                >
                    OTWARTE
                </ToggleButton>
                <ToggleButton
                    value={READY}
                    variant="outline-primary"
                    size={size || "xxl"}
                    onClick={() => onChange({ status: READY, end_date: null }, true)}
                >
                    GOTOWE
                </ToggleButton>
                <ToggleButton
                    value={DONE}
                    variant="outline-primary"
                    size={size || "xxl"}
                    onClick={() => {
                        if (commission.end_date === null) {
                            onChange({ status: DONE, end_date: new Date().toISOString().split("T")[0] }, true);
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
                    size={size || "xxl"}
                    onClick={() => onChange({ status: ON_HOLD, end_date: null }, true)}
                >
                    WSTRZYMANE
                </ToggleButton>
                <ToggleButton
                    value={CANCELLED}
                    variant="outline-primary"
                    size={size || "xxl"}
                    onClick={() => {
                        if (commission.end_date === null) {
                            onChange({ status: CANCELLED, end_date: new Date().toISOString().split("T")[0] }, true);
                        } else {
                            onChange({ status: CANCELLED }, true);
                        }
                    }}
                >
                    ANULOWANE
                </ToggleButton>
            </ToggleButtonGroup>
        </div>
    );
};

StatusButtons.propTypes = {
    onChange: PropTypes.func.isRequired,
    commission: PropTypes.object.isRequired,
    size: PropTypes.string,
};

export default StatusButtons;
