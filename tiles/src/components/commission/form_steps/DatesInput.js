import React, { useState } from "react";
import PropTypes from "prop-types";

import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import "../../../styles/big-datepicker.css";

import Form from "react-bootstrap/Form";
import { CANCELLED, DONE } from "../choices";
import Alert from "react-bootstrap/Alert";

const DatesInput = ({ currentStep, onChange, commission, errors }) => {
    if (currentStep !== 5) return null;

    const hasEndDate = commission.status === DONE || commission.status === CANCELLED;
    return (
        <>
            <div className="error-list">
                {errors.start_date
                    ? errors.start_date.map((error, idx) => (
                          <Alert key={idx} variant="danger">
                              {error}
                          </Alert>
                      ))
                    : null}
                {errors.end_date
                    ? errors.end_date.map((error, idx) => (
                          <Alert key={idx} variant="danger">
                              {error}
                          </Alert>
                      ))
                    : null}
            </div>
            <Form.Group className={`d-flex justify-content-${hasEndDate ? "between" : "center"} flex-wrap big-date`}>
                <div className="text-center">
                    <h2>Wybierz datę przyjęcia:</h2>
                    <DatePicker
                        selected={commission.start_date ? new Date(commission.start_date) : new Date()}
                        onChange={(date) => onChange({ start_date: date.toISOString().split("T")[0] }, !hasEndDate)}
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
                            selected={commission.end_date ? new Date(commission.end_date) : new Date()}
                            onChange={(date) => onChange({ end_date: date.toISOString().split("T")[0] }, true)}
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
        </>
    );
};

DatesInput.propTypes = {
    currentStep: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
    commission: PropTypes.object.isRequired,
};

export default DatesInput;
