import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";

import Form from "react-bootstrap/Form";
import { useLazyQuery, useMutation } from "@apollo/react-hooks";

import ContentLoading from "../common/ContentLoading";
import FormField from "../common/FormField";
import { COMPONENT_TYPE } from "./choices";

const COMPONENT = gql`
    query getComponent($filters: ComponentFilter) {
        components(filters: $filters) {
            objects {
                component_type
                model
                serial_number
                catalog_number
            }
        }
    }
`;

const ADD_COMPONENT = gql`
    mutation AddComponent($data: ComponentInput!) {
        addComponent(data: $data) {
            status
            errors {
                field
                message
            }
            object {
                id
                get_component_type_display
                model
                serial_number
                catalog_number
            }
        }
    }
`;

const UPDATE_COMPONENT = gql`
    mutation UpdateComponent($id: ID!, $data: ComponentInput!) {
        updateComponent(id: $id, data: $data) {
            status
            errors {
                field
                message
            }
            object {
                id
                get_component_type_display
                model
                serial_number
                catalog_number
            }
        }
    }
`;

const ComponentForm = (props) => {
    const [component, setComponent] = useState({
        component_type: props.initial ? props.initial.component_type : null,
        model: props.initial ? props.initial.model : null,
        serial_number: props.initial ? props.initial.serial_number : null,
        catalog_number: props.initial ? props.initial.catalog_number : null,
    });

    const [errors, setErrors] = useState({
        component_type: [],
        model: [],
        serial_number: [],
        catalog_number: [],
    });
    const [isLoading, setIsLoading] = useState(true);

    const [getComponent, { loading }] = useLazyQuery(COMPONENT, {
        variables: { filters: { id: props.componentId } },
        fetchPolicy: "no-cache",
        onCompleted: (data) => {
            const object = data.components.objects[0];
            setComponent({
                component_type: object.component_type,
                model: object.model,
                serial_number: object.serial_number,
                catalog_number: object.catalog_number,
            });
        },
    });

    const [addComponent] = useMutation(ADD_COMPONENT, {
        onCompleted: (data) => {
            if (data.addComponent.status === true) props.onSaved(data.addComponent.object);
            else {
                let newErrors = {};
                data.addComponent.errors.forEach((error) => {
                    if (newErrors[error.field]) newErrors[error.field].push(error.message);
                    else newErrors[error.field] = [error.message];
                });
                setErrors(newErrors);
            }
        },
    });

    const [updateComponent] = useMutation(UPDATE_COMPONENT, {
        onCompleted: (data) => {
            if (data.updateComponent.status === true) props.onSaved(data.updateComponent.object);
            else {
                let newErrors = {};
                data.updateComponent.errors.forEach((error) => {
                    if (newErrors[error.field]) newErrors[error.field].push(error.message);
                    else newErrors[error.field] = [error.message];
                });
                setErrors(newErrors);
            }
        },
    });

    useEffect(() => {
        if (props.componentId) getComponent();
        setIsLoading(false);
    }, [props.componentId]);

    const handleChanges = (e) => {
        setComponent({
            ...component,
            [e.target.name]:
                e.target.type === "number" ? (e.target.value ? Number(e.target.value) : null) : e.target.value,
        });
    };

    const onSubmit = (e) => {
        e.preventDefault();
        if (props.componentId) updateComponent({ variables: { id: props.componentId, data: component } });
        else addComponent({ variables: { data: component } });
    };

    if (isLoading || loading) return <ContentLoading />;

    return (
        <Form id="component-form" onSubmit={onSubmit} noValidate>
            <Form.Group controlId="formType">
                <FormField
                    label="Rodzaj podzespłu:"
                    name="component_type"
                    value={component.component_type}
                    onChange={handleChanges}
                    errors={errors.component_type}
                    type="select"
                    options={COMPONENT_TYPE}
                />
            </Form.Group>
            <Form.Group controlId="formModel">
                <FormField
                    label="Model:"
                    name="model"
                    value={component.model}
                    onChange={handleChanges}
                    errors={errors.model}
                />
            </Form.Group>
            <Form.Group controlId="formSerial">
                <FormField
                    label="Numer seryjny:"
                    name="serial_number"
                    value={component.serial_number}
                    onChange={handleChanges}
                    errors={errors.serial_number}
                />
            </Form.Group>
            <Form.Group controlId="formCatalog">
                <FormField
                    label="Numer katalogowy:"
                    name="catalog_number"
                    value={component.catalog_number}
                    onChange={handleChanges}
                    errors={errors.catalog_number}
                />
            </Form.Group>
        </Form>
    );
};

ComponentForm.propTypes = {
    componentId: PropTypes.string,
    initial: PropTypes.object,
    onSaved: PropTypes.func,
};

export default ComponentForm;
