import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { gql } from "apollo-boost";
import { useLazyQuery, useMutation } from "@apollo/react-hooks";
import { useHistory } from "react-router-dom";
import Swal from "sweetalert2";

import Button from "react-bootstrap/Button";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Container from "react-bootstrap/Container";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft, faArrowRight, faSave, faCheck } from "@fortawesome/free-solid-svg-icons";

import ContentLoading from "../common/ContentLoading";
import TypeInput from "./form_steps/TypeInput";
import VehicleInput from "./form_steps/VehicleInput";
import ComponentInput from "./form_steps/ComponentInput";
import ContractorInput from "./form_steps/ContractorInput";
import StatusInput from "./form_steps/StatusInput";
import DatesInput from "./form_steps/DatesInput";
import DescriptionInput from "./form_steps/DescriptionInput";
import ItemsInput from "./form_steps/ItemsInput";
import CommissionSummary from "./form_steps/CommissionSummary";
import { OPEN, VEHICLE } from "./choices";
import useDebounce from "../common/useDebounce";

const COMMISSION = gql`
    query getCommission($filters: CommissionFilter) {
        commissions(filters: $filters) {
            objects {
                id
                vc_name
                vehicle {
                    id
                }
                component {
                    id
                }
                commission_type
                status
                contractor {
                    id
                    name
                }
                description
                start_date
                end_date
                items {
                    id
                    name
                    description
                    quantity
                    price
                    ware {
                        id
                        index
                    }
                }
            }
        }
    }
`;

const ADD_COMMISSION = gql`
    mutation AddCommission($data: CommissionInput!) {
        addCommission(data: $data) {
            status
            errors {
                field
                message
                inline
                inline_id
            }
            object {
                id
                vc_name
            }
        }
    }
`;

const UPDATE_COMMISSION = gql`
    mutation UpdateCommission($id: ID!, $data: CommissionInput!) {
        updateCommission(id: $id, data: $data) {
            status
            errors {
                field
                message
                inline
                inline_id
            }
            object {
                id
                vc_name
            }
        }
    }
`;

const CommissionForm = (props) => {
    const STEP_COUNT = 8;
    const id = props.match.params.id;
    const history = useHistory();

    const [getCommission, { loading }] = useLazyQuery(COMMISSION, {
        variables: { filters: { id: id } },
        fetchPolicy: "no-cache",
        onCompleted: (data) => {
            const obj = data.commissions.objects[0];
            setCommission({
                commission_type: obj.commission_type,
                status: obj.status,
                vc_name: obj.vc_name,
                vehicle: obj.vehicle ? obj.vehicle.id : null,
                component: obj.component ? obj.component.id : null,
                contractor: obj.contractor ? obj.contractor.id : null,
                contractorLabel: obj.contractor ? obj.contractor.name : null,
                description: obj.description,
                start_date: obj.start_date,
                end_date: obj.end_date,
                items: obj.items.map((x) => ({
                    ...x,
                    ware: x.ware ? x.ware.id : null,
                    wareLabel: x.ware ? x.ware.index : null,
                })),
            });
            setCurrentStep(STEP_COUNT);
            setStepsStatus({
                1: true,
                2: true,
                3: true,
                4: true,
                5: true,
                6: true,
                7: true,
            });
        },
    });

    const handleErrors = (errors) => {
        let newErrors = {};
        errors.forEach((error) => {
            if (error.inline === "items") {
                if (newErrors.items === undefined) newErrors["items"] = {};
                if (newErrors.items[error.inline_id] === undefined) newErrors.items[error.inline_id] = {};
                if (newErrors.items[error.inline_id][error.field])
                    newErrors.items[error.inline_id][error.field].push(error.message);
                else newErrors.items[error.inline_id][error.field] = [error.message];
            } else {
                if (newErrors[error.field]) newErrors[error.field].push(error.message);
                else newErrors[error.field] = [error.message];
            }
        });
        setErrors(newErrors);
        Swal.fire({
            icon: "error",
            position: "top-end",
            showConfirmButton: false,
            timer: 5000,
            timerProgressBar: true,
            title: "Błąd!",
            text: "Popraw wprowadzone dane.",
            toast: true,
        });
    };

    const [addCommission] = useMutation(ADD_COMMISSION, {
        onCompleted: (data) => {
            if (data.addCommission.status === true) {
                Swal.fire({
                    icon: "success",
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 5000,
                    timerProgressBar: true,
                    title: "Sukces!",
                    text: "Zlecenie zostało zapisane.",
                    toast: true,
                });
                setErrors({});
                history.push(`/tiles/zlecenia/${data.addCommission.object.id}`);
            } else handleErrors(data.addCommission.errors);
        },
    });

    const [updateCommission] = useMutation(UPDATE_COMMISSION, {
        onCompleted: (data) => {
            if (data.updateCommission.status === true) {
                Swal.fire({
                    icon: "success",
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 5000,
                    timerProgressBar: true,
                    title: "Sukces!",
                    text: "Zmiany zostały zapisane.",
                    toast: true,
                });
                setErrors({});
            } else handleErrors(data.updateCommission.errors);
        },
    });

    const [currentStep, setCurrentStep] = useState(1);
    const [commission, setCommission] = useState({
        commission_type: VEHICLE,
        status: OPEN,
        vc_name: null,
        vehicle: null,
        component: null,
        contractor: null,
        contractorLabel: null,
        description: "",
        start_date: new Date().toISOString().split("T")[0],
        end_date: null,
        items: [],
    });
    const [errors, setErrors] = useState({});
    const [stepsStatus, setStepsStatus] = useState({
        1: false,
        2: false,
        3: false,
        4: false,
        5: false,
        6: false,
        7: false,
    });
    const [objectID, setObjectID] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    const debouncedCommission = useDebounce(commission, 3000, () => {
        if (id && !isLoading && !loading)
            updateCommission({
                variables: {
                    id: id,
                    data: {
                        ...commission,
                        contractorLabel: undefined,
                        __typename: undefined,
                        items: commission.items.map((x) => ({ ...x, wareLabel: undefined, __typename: undefined })),
                    },
                },
            });
    });

    useEffect(() => {
        const id = props.match.params.id;
        if (id !== undefined) {
            setObjectID(id);
            getCommission({ variables: { filters: { id: id } } });
        }
        setIsLoading(false);
    }, [props.match.params.id]);

    if (isLoading || loading) return <ContentLoading />;

    const handleChanges = (changes, next) => {
        setCommission({
            ...commission,
            ...changes,
        });
        if (next) nextStep();
    };

    const handleItemChanges = (index, changes) => {
        setCommission({
            ...commission,
            items: [
                ...commission.items.slice(0, index),
                {
                    ...commission.items[index],
                    ...changes,
                },
                ...commission.items.slice(index + 1),
            ],
        });
    };

    const handleAddItem = (item) => {
        setCommission({
            ...commission,
            items: [...commission.items, item],
        });
    };

    const handleRemoveItem = (index) => {
        setCommission({
            ...commission,
            items: [...commission.items.slice(0, index), ...commission.items.slice(index + 1)],
        });
    };

    const handleSubmit = () => {
        addCommission({
            variables: {
                data: {
                    ...commission,
                    contractorLabel: undefined,
                    items: commission.items.map((x) => ({ ...x, wareLabel: undefined })),
                },
            },
        });
    };

    const nextStep = () => {
        setStepsStatus({
            ...stepsStatus,
            [currentStep]: true,
        });
        const step = currentStep >= STEP_COUNT - 1 ? STEP_COUNT : currentStep + 1;
        setCurrentStep(step);
    };

    const previousStep = () => {
        setStepsStatus({
            ...stepsStatus,
            [currentStep]: true,
        });
        const step = currentStep <= 1 ? 1 : currentStep - 1;
        setCurrentStep(step);
    };

    const goToStep = (step) => {
        setStepsStatus({
            ...stepsStatus,
            [currentStep]: true,
        });
        if (step >= 1 && step <= STEP_COUNT) setCurrentStep(step);
    };

    return (
        <Container fluid>
            <Link className="back-button" to="/tiles">
                <Button variant="outline-primary" size="xl">
                    Wróć do listy zleceń
                </Button>
            </Link>
            <div>
                <div className="form-step-buttons">
                    <Button
                        variant="outline-dark"
                        size="xl"
                        type="button"
                        onClick={previousStep}
                        disabled={currentStep === 1}
                    >
                        <FontAwesomeIcon icon={faArrowLeft} /> Wstecz
                    </Button>
                    <div className="text-center">
                        <h1>{id ? `Edycja zlecenia ${id}` : "Nowe zlecenie"}</h1>
                        <ButtonGroup>
                            <Button
                                size="xl"
                                variant={
                                    errors.commission_type !== undefined
                                        ? "outline-danger"
                                        : stepsStatus[1]
                                        ? "outline-success"
                                        : "outline-dark"
                                }
                                active={currentStep == 1}
                                onClick={() => goToStep(1)}
                            >
                                Typ
                            </Button>
                            <Button
                                size="xl"
                                variant={
                                    errors.commission !== undefined ||
                                    errors.vehicle !== undefined ||
                                    errors.vc_name !== undefined
                                        ? "outline-danger"
                                        : stepsStatus[2] && commission.vc_name !== null
                                        ? "outline-success"
                                        : "outline-dark"
                                }
                                active={currentStep == 2}
                                onClick={() => goToStep(2)}
                            >
                                {commission.commission_type === VEHICLE ? "Pojazd" : "Podzespół"}
                            </Button>
                            <Button
                                size="xl"
                                variant={
                                    errors.contractor !== undefined
                                        ? "outline-danger"
                                        : stepsStatus[3] && commission.contractor !== null
                                        ? "outline-success"
                                        : "outline-dark"
                                }
                                active={currentStep == 3}
                                onClick={() => goToStep(3)}
                            >
                                Kontrahent
                            </Button>
                            <Button
                                size="xl"
                                variant={
                                    errors.status !== undefined
                                        ? "outline-danger"
                                        : stepsStatus[4] && commission.status !== null
                                        ? "outline-success"
                                        : "outline-dark"
                                }
                                active={currentStep == 4}
                                onClick={() => goToStep(4)}
                            >
                                Status
                            </Button>
                            <Button
                                size="xl"
                                variant={
                                    errors.start_date !== undefined || errors.end_date !== undefined
                                        ? "outline-danger"
                                        : stepsStatus[5] && commission.start_date !== null
                                        ? "outline-success"
                                        : "outline-dark"
                                }
                                active={currentStep == 5}
                                onClick={() => goToStep(5)}
                            >
                                Data
                            </Button>
                            <Button
                                size="xl"
                                variant={
                                    errors.description !== undefined
                                        ? "outline-danger"
                                        : stepsStatus[6]
                                        ? "outline-success"
                                        : "outline-dark"
                                }
                                active={currentStep == 6}
                                onClick={() => goToStep(6)}
                            >
                                Opis
                            </Button>
                            <Button
                                size="xl"
                                variant={
                                    errors.items !== undefined
                                        ? "outline-danger"
                                        : stepsStatus[7]
                                        ? "outline-success"
                                        : "outline-dark"
                                }
                                active={currentStep == 7}
                                onClick={() => goToStep(7)}
                            >
                                Pozycje
                            </Button>
                            <Button
                                size="xl"
                                variant="outline-info"
                                active={currentStep == 8}
                                onClick={() => goToStep(8)}
                            >
                                Podsumowanie
                            </Button>
                        </ButtonGroup>
                    </div>
                    <Button
                        variant="outline-dark"
                        size="xl"
                        type="button"
                        onClick={nextStep}
                        disabled={currentStep === STEP_COUNT}
                    >
                        Dalej <FontAwesomeIcon icon={faArrowRight} />
                    </Button>
                </div>
                <div>
                    <TypeInput
                        currentStep={currentStep}
                        commission={commission}
                        onChange={handleChanges}
                        errors={errors}
                    />
                    {commission.commission_type === VEHICLE ? (
                        <VehicleInput
                            currentStep={currentStep}
                            onChange={handleChanges}
                            commission={commission}
                            errors={errors}
                        />
                    ) : (
                        <ComponentInput
                            currentStep={currentStep}
                            onChange={handleChanges}
                            commission={commission}
                            errors={errors}
                        />
                    )}
                    <ContractorInput
                        currentStep={currentStep}
                        onChange={handleChanges}
                        commission={commission}
                        errors={errors}
                    />
                    <StatusInput
                        currentStep={currentStep}
                        onChange={handleChanges}
                        commission={commission}
                        errors={errors}
                    />
                    <DatesInput
                        currentStep={currentStep}
                        onChange={handleChanges}
                        commission={commission}
                        errors={errors}
                    />
                    <DescriptionInput
                        currentStep={currentStep}
                        onChange={handleChanges}
                        commission={commission}
                        errors={errors}
                    />
                    <ItemsInput
                        currentStep={currentStep}
                        onChange={handleItemChanges}
                        addItem={handleAddItem}
                        removeItem={handleRemoveItem}
                        commission={commission}
                        errors={errors}
                    />
                    <CommissionSummary currentStep={currentStep} commission={commission} />

                    {currentStep === STEP_COUNT && id === undefined ? (
                        <Button className="flex-align-end" variant="outline-success" size="xxl" onClick={handleSubmit}>
                            <FontAwesomeIcon icon={faSave} /> Zapisz
                        </Button>
                    ) : null}
                </div>
            </div>
        </Container>
    );
};

CommissionForm.propTypes = {};

export default CommissionForm;
