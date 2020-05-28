import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import ToggleButtonGroup from "react-bootstrap/ToggleButtonGroup";
import ToggleButton from "react-bootstrap/ToggleButton";
import { CANCELLED, DONE, ON_HOLD, OPEN, READY } from "../choices";
import Swal from "sweetalert2";
import { gql } from "apollo-boost";
import { useLazyQuery, useMutation } from "@apollo/react-hooks";
import Alert from "react-bootstrap/Alert";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import faInfoCircle from "@fortawesome/free-solid-svg-icons/faInfoCircle";

const CONTRACTOR = gql`
    query getContractor($filters: ContractorFilter) {
        contractors(filters: $filters) {
            objects {
                phone_1
                phone_2
            }
        }
    }
`;

const SEND_SMS = gql`
    mutation sendSMS($pk: ID!, $phone: String!) {
        sendCommissionNotification(pk: $pk, phone: $phone) {
            status
            message
        }
    }
`;

const StatusButtons = ({ onChange, commission, size }) => {
    const [getContractor, { loading, data }] = useLazyQuery(CONTRACTOR, {
        fetchPolicy: "no-cache",
        onCompleted: (contractor) => {
            let phonesTemp = [];
            if (contractor.contractors.objects[0].phone_1) phonesTemp.push(contractor.contractors.objects[0].phone_1);
            if (contractor.contractors.objects[0].phone_2) phonesTemp.push(contractor.contractors.objects[0].phone_2);
            setPhones(phonesTemp);
        },
    });
    const [phones, setPhones] = useState([]);

    useEffect(() => {
        if (commission.contractor && commission.id) {
            getContractor({ variables: { filters: { id: commission.contractor } } });
        }
    }, [commission.contractor]);

    const [sendSMS] = useMutation(SEND_SMS, {
        onCompleted: (data) => {
            if (data.sendCommissionNotification.status === true) {
                Swal.fire({
                    icon: "success",
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 5000,
                    timerProgressBar: true,
                    title: "Sukces!",
                    text: data.sendCommissionNotification.message,
                    toast: true,
                });
            } else {
                Swal.fire({
                    icon: "error",
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 5000,
                    timerProgressBar: true,
                    title: "Błąd!",
                    text: data.sendCommissionNotification.message,
                    toast: true,
                });
            }
        },
    });

    return (
        <div>
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
                        onClick={() => {
                            if (commission.id && phones.length > 0) {
                                Swal.fire({
                                    icon: "question",
                                    showConfirmButton: true,
                                    showCancelButton: true,
                                    title: "Czy chcesz wysłać powiadomienie SMS do klienta?",
                                    cancelButtonText: "Nie",
                                    confirmButtonText: "Tak",
                                    input: "radio",
                                    inputOptions: phones.reduce((obj, phone) => {
                                        obj[phone] = phone;
                                        return obj;
                                    }, {}),
                                    inputValue: phones[0],
                                }).then(({ value }) => {
                                    if (value) {
                                        sendSMS({ variables: { pk: commission.id, phone: value } });
                                    }
                                    onChange({ status: READY, end_date: null }, true);
                                });
                            } else {
                                onChange({ status: READY, end_date: null }, true);
                            }
                        }}
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
            {commission.sent_sms ? (
                <Alert className="mt-3 mb-0" variant="info">
                    <div className="d-flex align-items-center">
                        <FontAwesomeIcon icon={faInfoCircle} size="2x" className="mr-2" />
                        Powiadomienie SMS zostało już wysłane.
                    </div>
                </Alert>
            ) : null}
        </div>
    );
};

StatusButtons.propTypes = {
    onChange: PropTypes.func.isRequired,
    commission: PropTypes.object.isRequired,
    size: PropTypes.string,
};

export default StatusButtons;
