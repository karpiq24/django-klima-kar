import React, { useState, useRef } from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useQuery, useLazyQuery } from "@apollo/react-hooks";

import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import Alert from "react-bootstrap/Alert";
import Modal from "react-bootstrap/Modal";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faQrcode } from "@fortawesome/free-solid-svg-icons/faQrcode";
import { faEdit } from "@fortawesome/free-solid-svg-icons/faEdit";

import ContentLoading from "../../common/ContentLoading";
import InfiniteSelect from "../../common/InfiniteSelect";
import useDebounce from "../../common/useDebounce";
import ModalForm from "../../common/ModalForm";
import VehicleForm from "../VehicleForm";
import { genericError } from "../../../utils";

const VehicleInput = ({ currentStep, commission, onChange, errors }) => {
    if (currentStep !== 2) return null;

    const VEHICLES = gql`
        query getVehicles($pagination: PageInput, $filters: VehicleFilter, $search: String) {
            vehicles(pagination: $pagination, filters: $filters, search: $search) {
                pageInfo {
                    hasPreviousPage
                    hasNextPage
                    numPages
                    count
                    pageNumber
                }
                objects {
                    id
                    registration_plate
                    brand
                    model
                    production_year
                }
            }
        }
    `;

    const DECODE_SCANNDED = gql`
        query decodeScanned($code: String!, $create: Boolean!) {
            decode(code: $code, create: $create) {
                pk
                label
            }
        }
    `;

    const { loading, data, fetchMore, refetch } = useQuery(VEHICLES, {
        variables: {
            pagination: { page: 1 },
            filters: {},
        },
    });

    const [decodeScanned] = useLazyQuery(DECODE_SCANNDED, {
        onCompleted: (data) => {
            setShowScanModal(false);
            if (data.decode === null) {
                genericError();
            } else if (data.decode.pk && data.decode.label) {
                onChange(
                    {
                        vehicle: data.decode.pk,
                        vc_name: data.decode.label,
                    },
                    true
                );
            }
        },
    });

    const [createInitial, setCreateInitial] = useState(null);
    const [showFormModal, setShowFormModal] = useState(false);
    const [showScanModal, setShowScanModal] = useState(false);
    const [code, setCode] = useState("");
    const debouncedCode = useDebounce(code, 300, () => decodeScanned({ variables: { code: code, create: true } }));
    const scanRef = useRef(null);

    const loadVehicles = (page) => {
        fetchMore({
            variables: {
                pagination: { page: page },
            },
            updateQuery: (prev, { fetchMoreResult }) => {
                if (!fetchMoreResult) return prev;
                return {
                    ...data,
                    vehicles: {
                        ...data.vehicles,
                        pageInfo: {
                            ...fetchMoreResult.vehicles.pageInfo,
                        },
                        objects: [...prev.vehicles.objects, ...fetchMoreResult.vehicles.objects],
                    },
                };
            },
        });
    };

    const hadnleScanCode = () => {
        setShowScanModal(true);
        setTimeout(() => {
            scanRef.current.focus();
        }, 100);
    };

    return (
        <>
            {data === undefined ? (
                <ContentLoading />
            ) : (
                <>
                    <div className="error-list">
                        {errors.vehicle
                            ? errors.vehicle.map((error, idx) => (
                                  <Alert key={idx} variant="danger">
                                      {error}
                                  </Alert>
                              ))
                            : null}
                        {errors.vc_name
                            ? errors.vc_name.map((error, idx) => (
                                  <Alert key={idx} variant="danger">
                                      {error}
                                  </Alert>
                              ))
                            : null}
                    </div>
                    <div className="d-flex justify-content-between vehicle-container vehicle-select">
                        <Form.Group className="w-100">
                            <h2>Wybierz pojazd:</h2>
                            <div className="d-flex">
                                <InfiniteSelect
                                    refetch={(value) =>
                                        refetch({
                                            search: value.trim(),
                                            pagination: { page: 1 },
                                        })
                                    }
                                    searchPlaceholder="Podaj numer rejestracyjny"
                                    createLabel="Dodaj nowy pojazd"
                                    autoFocus={true}
                                    show={true}
                                    loadMore={loadVehicles}
                                    hasMore={data.vehicles.pageInfo.hasNextPage}
                                    objects={data.vehicles.objects}
                                    getObjectLabel={(vehicle) =>
                                        [
                                            vehicle.brand,
                                            vehicle.model,
                                            vehicle.registration_plate,
                                            vehicle.production_year ? `(${vehicle.production_year})` : null,
                                        ]
                                            .filter(Boolean)
                                            .join(" ")
                                    }
                                    selected={commission.vehicle}
                                    selectedLabel={commission.vc_name}
                                    onCreate={(value) => {
                                        setCreateInitial({ registration_plate: value });
                                        setShowFormModal(true);
                                    }}
                                    onChange={(value, label) =>
                                        onChange(
                                            {
                                                vehicle: value,
                                                vc_name: label,
                                            },
                                            value ? true : false
                                        )
                                    }
                                />
                                {commission.vehicle ? (
                                    <Button
                                        variant="warning"
                                        size="lg"
                                        className="ml-2 d-flex align-items-center"
                                        onClick={() => setShowFormModal(true)}
                                    >
                                        <FontAwesomeIcon className="mr-2" icon={faEdit} />
                                        Edytuj
                                    </Button>
                                ) : null}
                            </div>
                        </Form.Group>
                        <p></p>
                        <Form.Group className="w-100 text-center">
                            <h2>Zeskanuj dowód rejestracyjny:</h2>
                            <Button size="xxl" onClick={hadnleScanCode}>
                                <FontAwesomeIcon icon={faQrcode} size="10x" />
                            </Button>
                        </Form.Group>
                    </div>
                    <ModalForm
                        show={showFormModal}
                        onHide={() => setShowFormModal(false)}
                        formId="vehicle-form"
                        title={createInitial ? "Dodaj nowy pojazd" : "Edycja pojazdu"}
                    >
                        <VehicleForm
                            vehicleId={createInitial ? null : commission.vehicle}
                            initial={createInitial}
                            onSaved={(vehicle) =>
                                onChange(
                                    {
                                        vehicle: vehicle.id,
                                        vc_name: [
                                            vehicle.brand,
                                            vehicle.model,
                                            vehicle.registration_plate,
                                            vehicle.production_year ? `(${vehicle.production_year})` : null,
                                        ]
                                            .filter(Boolean)
                                            .join(" "),
                                    },
                                    true
                                )
                            }
                        />
                    </ModalForm>
                    <Modal show={showScanModal} centered size="lg" onHide={() => setShowScanModal(false)}>
                        <Modal.Header>
                            <Modal.Title>Zeskanuj dowód rejestracyjny</Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            <Form.Control ref={scanRef} size="lg" onChange={(event) => setCode(event.target.value)} />
                        </Modal.Body>
                    </Modal>
                </>
            )}
        </>
    );
};

VehicleInput.propTypes = {
    currentStep: PropTypes.number.isRequired,
    commission: PropTypes.object.isRequired,
    onChange: PropTypes.func.isRequired,
};

export default VehicleInput;
