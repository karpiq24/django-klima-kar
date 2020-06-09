import React, { useState, useEffect } from "react";
import { gql } from "apollo-boost";
import { useLazyQuery, useMutation } from "@apollo/react-hooks";
import { useHistory } from "react-router-dom";
import Swal from "sweetalert2";

import Button from "react-bootstrap/Button";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Container from "react-bootstrap/Container";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft } from "@fortawesome/free-solid-svg-icons/faArrowLeft";
import { faArrowRight } from "@fortawesome/free-solid-svg-icons/faArrowRight";
import { faSave } from "@fortawesome/free-solid-svg-icons/faSave";

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
                sent_sms
                description
                start_date
                end_date
                is_editable
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
                id: obj.id,
                sent_sms: obj.sent_sms,
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
                is_editable: obj.is_editable,
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

        if (newErrors.commission_type) return goToStep(1);
        if (newErrors.component || newErrors.vehicle || newErrors.vc_name) return goToStep(2);
        if (newErrors.contractor) return goToStep(3);
        if (newErrors.status) return goToStep(4);
        if (newErrors.start_date || newErrors.end_date) return goToStep(5);
        if (newErrors.desc) return goToStep(6);
        if (newErrors.items) return goToStep(7);
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
                setIsSaved(true);
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
                setIsSaved(true);
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
        is_editable: true,
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
    const [isSaved, setIsSaved] = useState(true);

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
        if (!commission.is_editable) return;
        setCommission({
            ...commission,
            ...changes,
        });
        setIsSaved(false);
        if (next) nextStep();
    };

    const handleItemChanges = (index, changes) => {
        if (!commission.is_editable) return;
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
        setIsSaved(false);

        if (errors.items && errors.items[index]) {
            setErrors({
                ...errors,
                items: {
                    ...errors.items,
                    [index]: undefined,
                },
            });
        }
    };

    const handleAddItem = (item) => {
        if (!commission.is_editable) return;
        setCommission({
            ...commission,
            items: [...commission.items, item],
        });
        setIsSaved(false);
    };

    const handleRemoveItem = (index) => {
        if (!commission.is_editable) return;
        setCommission({
            ...commission,
            items: [...commission.items.slice(0, index), ...commission.items.slice(index + 1)],
        });
        setIsSaved(false);
        setErrors({
            ...errors,
            items: undefined,
        });
    };

    const handleSubmit = () => {
        if (!commission.is_editable) return;
        if (objectID) {
            updateCommission({
                variables: {
                    id: id,
                    data: {
                        ...commission,
                        id: undefined,
                        sent_sms: undefined,
                        contractorLabel: undefined,
                        is_editable: undefined,
                        __typename: undefined,
                        items: commission.items.map((x) => ({ ...x, wareLabel: undefined, __typename: undefined })),
                    },
                },
            });
        } else {
            addCommission({
                variables: {
                    data: {
                        ...commission,
                        contractorLabel: undefined,
                        is_editable: undefined,
                        items: commission.items.map((x) => ({ ...x, wareLabel: undefined })),
                    },
                },
            });
        }
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

    const handleBackButton = () => {
        if (!isSaved)
            Swal.fire({
                icon: "warning",
                showConfirmButton: true,
                showCancelButton: true,
                timerProgressBar: true,
                title: "Zlecenie nie zostało jeszcze zapisane!",
                text: "Na pewno opuścić formularz?",
                cancelButtonText: "Nie",
                confirmButtonText: "Tak",
            }).then(({ value }) => {
                if (value) history.push(`/tiles/`);
            });
        else history.push(`/tiles/`);
    };

    return (
        <Container fluid>
            <Button className="back-button" variant="outline-primary" size="xl" onClick={handleBackButton}>
                Wróć do listy zleceń
            </Button>
            <div>
                <div className="form-step-buttons">
                    <Button
                        variant="outline-dark"
                        size="xl"
                        type="button"
                        className="mr-2"
                        onClick={previousStep}
                        disabled={currentStep === 1}
                    >
                        <FontAwesomeIcon icon={faArrowLeft} />
                    </Button>
                    <div className="text-center">
                        <h1>
                            {id ? `Edycja zlecenia ${id}` : "Nowe zlecenie"}
                            {!commission.is_editable ? (
                                <p className="new-alert d-flex align-items-baseline justify-content-center mb-0">
                                    Zlecenie jest w trybie tylko do odczytu.
                                </p>
                            ) : null}
                            {isSaved ? null : (
                                <p className="new-alert d-flex align-items-baseline justify-content-center mb-0">
                                    {objectID
                                        ? "Zmiany nie zostały jeszcze zapisane."
                                        : "To zlecenie nie zostało jeszcze zapisane."}
                                    <Button
                                        className="flex-align-end ml-3"
                                        variant="outline-success"
                                        size="lg"
                                        onClick={handleSubmit}
                                    >
                                        <FontAwesomeIcon icon={faSave} /> Zapisz teraz
                                    </Button>
                                </p>
                            )}
                        </h1>
                        <ButtonGroup className="mt-4 pretty-select">
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
                                        : stepsStatus[6] && commission.description
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
                                        : stepsStatus[7] && commission.items.length > 0
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
                        className="ml-2"
                        onClick={nextStep}
                        disabled={currentStep === STEP_COUNT}
                    >
                        <FontAwesomeIcon icon={faArrowRight} />
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
                    <CommissionSummary currentStep={currentStep} commission={commission} onChange={handleChanges} />
                </div>
            </div>
        </Container>
    );
};

CommissionForm.propTypes = {};

export default CommissionForm;
