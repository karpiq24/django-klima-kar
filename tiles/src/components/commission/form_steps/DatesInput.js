import React, { useState } from "react";
import PropTypes from "prop-types";

import Form from "react-bootstrap/Form";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import "../../../styles/big-datepicker.css";

const DatesInput = ({ currentStep, onChange, commission }) => {
    if (currentStep !== 5) return null;

    const hasEndDate = commission.status === "DO" || commission.status === "CA";
    return (
        <Form.Group className={`d-flex justify-content-${hasEndDate ? "between" : "center"} flex-wrap`}>
            <div className="text-center">
                <h2>Wybierz datę przyjęcia:</h2>
                <DatePicker
                    selected={commission.start_date}
                    onChange={date => onChange({ start_date: date }, !hasEndDate)}
                    todayButton="Dzisiaj"
                    placeholderText="Wybierz datę"
                    showMonthDropdown
                    showYearDropdown
                    fixedHeight
                    inline
                />
            </div>
            {hasEndDate ? (
                <div className="text-center">
                    <h2>Wybierz datę zakończenia:</h2>
                    <DatePicker
                        selected={commission.end_date}
                        onChange={date => onChange({ end_date: date }, true)}
                        todayButton="Dzisiaj"
                        placeholderText="Wybierz datę"
                        showMonthDropdown
                        showYearDropdown
                        fixedHeight
                        inline
                    />
                </div>
            ) : null}
        </Form.Group>
    );
};

DatesInput.propTypes = {
    currentStep: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
    commission: PropTypes.object.isRequired
};

export default DatesInput;
