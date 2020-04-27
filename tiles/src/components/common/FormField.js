import React from "react";
import PropTypes from "prop-types";

import Form from "react-bootstrap/Form";

import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAsterisk } from "@fortawesome/free-solid-svg-icons";

const FormField = (props) => {
    return (
        <div>
            {props.label ? (
                <Form.Label>
                    {props.label}
                    {props.required ? (
                        <FontAwesomeIcon className="ml-1 pb-1" icon={faAsterisk} color="red" size="xs" />
                    ) : null}
                </Form.Label>
            ) : null}
            {props.type === "date" ? (
                <DatePicker
                    className={`form-control form-control-lg ${
                        props.errors === undefined ? "is-valid" : props.errors.length > 0 ? "is-invalid" : ""
                    }`}
                    selected={props.value ? new Date(props.value) : null}
                    onChange={(date) =>
                        props.onChange({ target: { name: props.name, value: date.toISOString().split("T")[0] } })
                    }
                    todayButton="Dzisiaj"
                    dateFormat="yyyy-MM-dd"
                    showMonthDropdown
                    showYearDropdown
                    fixedHeight
                />
            ) : props.type === "select" ? (
                <Form.Control
                    className={props.className ? props.className : ""}
                    as="select"
                    name={props.name}
                    value={props.value || ""}
                    onChange={props.onChange}
                    size="lg"
                    isValid={props.errors === undefined}
                    isInvalid={props.errors !== undefined && props.errors.length > 0 ? true : false}
                >
                    <option key="null" value="">
                        ----------
                    </option>
                    {props.options.map((option) => (
                        <option key={option.key} value={option.key}>
                            {option.label}
                        </option>
                    ))}
                </Form.Control>
            ) : (
                <Form.Control
                    className={props.className ? props.className : ""}
                    name={props.name}
                    type={props.type}
                    step={props.step}
                    value={props.value === null || props.value === undefined ? "" : props.value}
                    onChange={props.onChange}
                    size="lg"
                    isValid={props.errors === undefined}
                    isInvalid={props.errors !== undefined && props.errors.length > 0 ? true : false}
                    placeholder={props.placeholder}
                />
            )}

            {props.errors !== undefined
                ? props.errors.map((error, idx) => (
                      <Form.Control.Feedback key={idx} type="invalid">
                          {error}
                      </Form.Control.Feedback>
                  ))
                : null}
        </div>
    );
};

FormField.propTypes = {
    label: PropTypes.string,
    name: PropTypes.string.isRequired,
    value: PropTypes.any,
    onChange: PropTypes.func.isRequired,
    errors: PropTypes.any,
    required: PropTypes.bool,
    type: PropTypes.string,
    options: PropTypes.array,
    placeholder: PropTypes.string,
    className: PropTypes.string,
    step: PropTypes.string
};

export default FormField;
