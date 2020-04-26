import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useLazyQuery, useMutation } from "@apollo/react-hooks";

import Form from "react-bootstrap/Form";
import Col from "react-bootstrap/Col";

import ContentLoading from "../common/ContentLoading";
import GusButton from "./GusButton";
import FormField from "../common/FormField";

const CONTRACTOR = gql`
    query getContractor($filters: ContractorFilter) {
        contractors(filters: $filters) {
            objects {
                name
                nip
                nip_prefix
                address_1
                address_2
                city
                postal_code
                email
                bdo_number
                phone_1
                phone_2
            }
        }
    }
`;

const ADD_CONTRACTOR = gql`
    mutation AddContractor($data: ContractorInput!) {
        addContractor(data: $data) {
            status
            errors {
                field
                message
            }
            object {
                id
                name
            }
        }
    }
`;

const UPDATE_CONTRACTOR = gql`
    mutation UpdateContractor($id: ID!, $data: ContractorInput!) {
        updateContractor(id: $id, data: $data) {
            status
            errors {
                field
                message
            }
            object {
                id
                name
            }
        }
    }
`;

const ContractorForm = (props) => {
    const [contractor, setContractor] = useState({
        nip_prefix: props.initial ? props.initial.nip_prefix : null,
        nip: props.initial ? props.initial.nip : null,
        name: props.initial ? props.initial.name : null,
        city: props.initial ? props.initial.city : null,
        address_1: props.initial ? props.initial.address_1 : null,
        address_2: props.initial ? props.initial.address_2 : null,
        city: props.initial ? props.initial.city : null,
        postal_code: props.initial ? props.initial.postal_code : null,
        email: props.initial ? props.initial.email : null,
        phone_1: props.initial ? props.initial.phone_1 : null,
        phone_2: props.initial ? props.initial.phone_2 : null,
        bdo_number: props.initial ? props.initial.bdo_number : null,
    });

    const [errors, setErrors] = useState({
        name: [],
        nip: [],
        nip_prefix: [],
        address_1: [],
        address_2: [],
        city: [],
        postal_code: [],
        email: [],
        bdo_number: [],
        phone_1: [],
        phone_2: [],
    });
    const [isLoading, setIsLoading] = useState(true);

    const [getContractor, { loading }] = useLazyQuery(CONTRACTOR, {
        variables: { filters: { id: props.contractorId } },
        fetchPolicy: "no-cache",
        onCompleted: (data) => {
            const object = data.contractors.objects[0];
            setContractor({
                name: object.name,
                nip: object.nip,
                nip_prefix: object.nip_prefix,
                address_1: object.address_1,
                address_2: object.address_2,
                city: object.city,
                postal_code: object.postal_code,
                email: object.email,
                bdo_number: object.bdo_number,
                phone_1: object.phone_1,
                phone_2: object.phone_2,
            });
        },
    });

    const [addContractor] = useMutation(ADD_CONTRACTOR, {
        onCompleted: (data) => {
            if (data.addContractor.status === true) props.onSaved(data.addContractor.object);
            else {
                let newErrors = {};
                data.addContractor.errors.forEach((error) => {
                    if (newErrors[error.field]) newErrors[error.field].push(error.message);
                    else newErrors[error.field] = [error.message];
                });
                setErrors(newErrors);
            }
        },
    });

    const [updateContractor] = useMutation(UPDATE_CONTRACTOR, {
        onCompleted: (data) => {
            if (data.updateContractor.status === true) props.onSaved(data.updateContractor.object);
            else {
                let newErrors = {};
                data.updateContractor.errors.forEach((error) => {
                    if (newErrors[error.field]) newErrors[error.field].push(error.message);
                    else newErrors[error.field] = [error.message];
                });
                setErrors(newErrors);
            }
        },
    });

    useEffect(() => {
        if (props.contractorId) getContractor();
        setIsLoading(false);
    }, [props.contractorId]);

    const handleChanges = (e) => {
        setContractor({
            ...contractor,
            [e.target.name]: e.target.value,
        });
    };

    const onSubmit = (e) => {
        e.preventDefault();
        if (props.contractorId) updateContractor({ variables: { id: props.contractorId, data: contractor } });
        else addContractor({ variables: { data: contractor } });
    };

    if (isLoading || loading) return <ContentLoading />;

    return (
        <Form id="contractor-form" onSubmit={onSubmit} noValidate>
            <Form.Row>
                <Form.Group as={Col} controlId="formNipPrefix" xs="3" sm="2">
                    <FormField
                        label="Prefiks:"
                        name="nip_prefix"
                        value={contractor.nip_prefix}
                        onChange={handleChanges}
                        errors={errors.nip_prefix}
                    />
                </Form.Group>
                <Form.Group as={Col} controlId="formNip">
                    <div className="d-flex align-items-end">
                        <div className="w-100">
                            <FormField
                                label="NIP:"
                                name="nip"
                                value={contractor.nip}
                                onChange={handleChanges}
                                errors={errors.nip}
                            />
                        </div>
                        <div className="ml-2">
                            <GusButton
                                nip={contractor.nip}
                                onCompleted={(data) =>
                                    setContractor({
                                        ...contractor,
                                        name: data.name,
                                        city: data.city,
                                        postal_code: data.postal_code,
                                        address_1: data.street_address,
                                    })
                                }
                            />
                        </div>
                    </div>
                </Form.Group>
            </Form.Row>
            <Form.Group controlId="formName">
                <FormField
                    label="Nazwa:"
                    name="name"
                    required={true}
                    value={contractor.name}
                    onChange={handleChanges}
                    errors={errors.name}
                />
            </Form.Group>
            <Form.Row>
                <Form.Group as={Col} controlId="formPostalCode" sm="4" md="3">
                    <FormField
                        label="Kod pocztowy:"
                        name="postal_code"
                        value={contractor.postal_code}
                        onChange={handleChanges}
                        errors={errors.postal_code}
                    />
                </Form.Group>
                <Form.Group as={Col} controlId="formCity">
                    <FormField
                        label="Miasto:"
                        name="city"
                        value={contractor.city}
                        onChange={handleChanges}
                        errors={errors.city}
                    />
                </Form.Group>
            </Form.Row>
            <Form.Group controlId="formAddress1">
                <FormField
                    label="Adres:"
                    name="address_1"
                    value={contractor.address_1}
                    onChange={handleChanges}
                    errors={errors.address_1}
                />
            </Form.Group>
            <Form.Group controlId="formAddress2">
                <FormField
                    label="Adres 2:"
                    name="address_2"
                    value={contractor.address_2}
                    onChange={handleChanges}
                    errors={errors.address_2}
                />
            </Form.Group>
            <Form.Group controlId="formEmail">
                <FormField
                    label="Adres e-mail:"
                    name="email"
                    value={contractor.email}
                    onChange={handleChanges}
                    errors={errors.email}
                />
            </Form.Group>
            <Form.Row>
                <Form.Group as={Col} controlId="formPhone1" sm="6">
                    <FormField
                        label="Numer telefonu:"
                        name="phone_1"
                        value={contractor.phone_1}
                        onChange={handleChanges}
                        errors={errors.phone_1}
                    />
                </Form.Group>
                <Form.Group as={Col} controlId="formPhone2" sm="6">
                    <FormField
                        label="Numer telefonu 2:"
                        name="phone_2"
                        value={contractor.phone_2}
                        onChange={handleChanges}
                        errors={errors.phone_2}
                    />
                </Form.Group>
            </Form.Row>
            <Form.Group controlId="formBDO">
                <FormField
                    label="Numer BDO:"
                    name="bdo_number"
                    value={contractor.bdo_number}
                    onChange={handleChanges}
                    errors={errors.bdo_number}
                />
            </Form.Group>
        </Form>
    );
};

ContractorForm.propTypes = {
    contractorId: PropTypes.string,
    initial: PropTypes.object,
    onSaved: PropTypes.func,
};

export default ContractorForm;
