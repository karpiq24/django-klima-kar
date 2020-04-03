import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { gql } from "apollo-boost";
import { useLazyQuery } from "@apollo/react-hooks";

import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft, faArrowRight, faSave, faMailBulk } from "@fortawesome/free-solid-svg-icons";

import ContentLoading from "../common/ContentLoading";
import TypeInput from "./form_steps/TypeInput";
import VehicleForm from "./form_steps/VehicleForm";
import ComponentForm from "./form_steps/ComponentForm";
import ContractorForm from "./form_steps/ContractorForm";
import StatusInput from "./form_steps/StatusInput";
import DatesInput from "./form_steps/DatesInput";
import DescriptionInput from "./form_steps/DescriptionInput";
import ItemsInput from "./form_steps/ItemsInput";
import CommissionSummary from "./form_steps/CommissionSummary";

const CommissionForm = props => {
    const STEP_COUNT = 8;
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
                    value
                    items {
                        name
                        description
                        quantity
                        price
                    }
                }
            }
        }
    `;
    const id = props.match.params.id;
    const [getCommission, { loading, data }] = useLazyQuery(COMMISSION, {
        variables: { filters: { id: id } },
        fetchPolicy: "no-cache",
        onCompleted: data => {
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
                start_date: new Date(obj.start_date),
                end_date: obj.end_date ? new Date(obj.end_date) : null,
                items: obj.items
            });
            setCurrentStep(STEP_COUNT);
        }
    });

    const [currentStep, setCurrentStep] = useState(1);
    const [commission, setCommission] = useState({
        commission_type: "VEHICLE",
        status: "OPEN",
        vc_name: null,
        vehicle: null,
        component: null,
        contractor: null,
        contractorLabel: null,
        description: "",
        start_date: new Date(),
        end_date: null,
        items: [],
        value: 0
    });
    const [objectID, setObjectID] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const id = props.match.params.id;
        if (id !== undefined) {
            setObjectID(id);
            getCommission({ variables: { filters: { id: id } } });
        }
        setIsLoading(false);
    }, []);

    if (isLoading || loading) return <ContentLoading />;

    const handleChanges = (changes, next) => {
        setCommission({
            ...commission,
            ...changes
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
                    ...changes
                },
                ...commission.items.slice(index + 1)
            ]
        });
    };

    const handleAddItem = item => {
        setCommission({
            ...commission,
            items: [...commission.items, item]
        });
    };

    const handleRemoveItem = index => {
        setCommission({
            ...commission,
            items: [...commission.items.slice(0, index), ...commission.items.slice(index + 1)]
        });
    };

    const handleSubmit = event => {
        event.preventDefault();
        console.log(commission);
    };

    const nextStep = () => {
        const step = currentStep >= STEP_COUNT - 1 ? STEP_COUNT : currentStep + 1;
        setCurrentStep(step);
    };

    const previousStep = () => {
        const step = currentStep <= 1 ? 1 : currentStep - 1;
        setCurrentStep(step);
    };

    const goToStep = step => {
        if (step >= 1 && step <= STEP_COUNT) setCurrentStep(step);
    };

    return (
        <>
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
                        Krok {currentStep} z {STEP_COUNT}
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
                <Form onSubmit={handleSubmit}>
                    <TypeInput currentStep={currentStep} onChange={handleChanges} />
                    {commission.commission_type === "VH" ? (
                        <VehicleForm currentStep={currentStep} onChange={handleChanges} commission={commission} />
                    ) : (
                        <ComponentForm currentStep={currentStep} onChange={handleChanges} commission={commission} />
                    )}
                    <ContractorForm currentStep={currentStep} onChange={handleChanges} commission={commission} />
                    <StatusInput currentStep={currentStep} onChange={handleChanges} commission={commission} />
                    <DatesInput currentStep={currentStep} onChange={handleChanges} commission={commission} />
                    <DescriptionInput currentStep={currentStep} onChange={handleChanges} commission={commission} />
                    <ItemsInput
                        currentStep={currentStep}
                        onChange={handleItemChanges}
                        addItem={handleAddItem}
                        removeItem={handleRemoveItem}
                        commission={commission}
                    />
                    <CommissionSummary currentStep={currentStep} commission={commission} />

                    {currentStep === STEP_COUNT ? (
                        <Button className="flex-align-end" variant="outline-success" size="xxl" type="submit" disabled>
                            <FontAwesomeIcon icon={faSave} /> Zapisz
                        </Button>
                    ) : null}
                </Form>
            </div>
        </>
    );
};

CommissionForm.propTypes = {};

export default CommissionForm;