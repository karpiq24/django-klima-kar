import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useLazyQuery, useMutation } from "@apollo/react-hooks";

import Form from "react-bootstrap/Form";
import Col from "react-bootstrap/Col";

import ContentLoading from "../common/ContentLoading";
import FormField from "../common/FormField";
import { FUEL_TYPE } from "./choices";

const VEHICLE = gql`
    query getVehicle($filters: VehicleFilter) {
        vehicles(filters: $filters) {
            objects {
                registration_plate
                vin
                brand
                model
                engine_volume
                engine_power
                production_year
                registration_date
                fuel_type
            }
        }
    }
`;

const ADD_VEHICLE = gql`
    mutation AddVehicle($data: VehicleInput!) {
        addVehicle(data: $data) {
            status
            errors {
                field
                message
            }
            object {
                id
                registration_plate
                brand
                model
                production_year
            }
        }
    }
`;

const UPDATE_VEHICLE = gql`
    mutation UpdateVehicle($id: ID!, $data: VehicleInput!) {
        updateVehicle(id: $id, data: $data) {
            status
            errors {
                field
                message
            }
            object {
                id
                registration_plate
                brand
                model
                production_year
            }
        }
    }
`;

const VehicleForm = (props) => {
    const [vehicle, setVehicle] = useState({
        registration_plate: props.initial ? props.initial.registration_plate : null,
        vin: props.initial ? props.initial.vin : null,
        brand: props.initial ? props.initial.brand : null,
        model: props.initial ? props.initial.model : null,
        engine_volume: props.initial ? props.initial.engine_volume : null,
        engine_power: props.initial ? props.initial.engine_power : null,
        production_year: props.initial ? props.initial.production_year : null,
        registration_date: props.initial ? props.initial.registration_date : null,
        fuel_type: props.initial ? props.initial.fuel_type : null,
    });

    const [errors, setErrors] = useState({
        registration_plate: [],
        vin: [],
        brand: [],
        model: [],
        engine_volume: [],
        engine_power: [],
        production_year: [],
        registration_date: [],
        fuel_type: [],
    });
    const [isLoading, setIsLoading] = useState(true);

    const [getVehicle, { loading }] = useLazyQuery(VEHICLE, {
        variables: { filters: { id: props.vehicleId } },
        fetchPolicy: "no-cache",
        onCompleted: (data) => {
            const object = data.vehicles.objects[0];
            setVehicle({
                registration_plate: object.registration_plate,
                vin: object.vin,
                brand: object.brand,
                model: object.model,
                engine_volume: object.engine_volume,
                engine_power: object.engine_power,
                production_year: object.production_year,
                registration_date: object.registration_date,
                fuel_type: object.fuel_type,
            });
        },
    });

    const [addVehicle] = useMutation(ADD_VEHICLE, {
        onCompleted: (data) => {
            if (data.addVehicle.status === true) props.onSaved(data.addVehicle.object);
            else {
                let newErrors = {};
                data.addVehicle.errors.forEach((error) => {
                    if (newErrors[error.field]) newErrors[error.field].push(error.message);
                    else newErrors[error.field] = [error.message];
                });
                setErrors(newErrors);
            }
        },
    });

    const [updateVehicle] = useMutation(UPDATE_VEHICLE, {
        onCompleted: (data) => {
            if (data.updateVehicle.status === true) props.onSaved(data.updateVehicle.object);
            else {
                let newErrors = {};
                data.updateVehicle.errors.forEach((error) => {
                    if (newErrors[error.field]) newErrors[error.field].push(error.message);
                    else newErrors[error.field] = [error.message];
                });
                setErrors(newErrors);
            }
        },
    });

    useEffect(() => {
        if (props.vehicleId) getVehicle();
        setIsLoading(false);
    }, [props.vehicleId]);

    const handleChanges = (e) => {
        setVehicle({
            ...vehicle,
            [e.target.name]:
                e.target.type === "number" ? (e.target.value ? Number(e.target.value) : null) : e.target.value,
        });
    };

    const onSubmit = (e) => {
        e.preventDefault();
        if (props.vehicleId) updateVehicle({ variables: { id: props.vehicleId, data: vehicle } });
        else addVehicle({ variables: { data: vehicle } });
    };

    if (isLoading || loading) return <ContentLoading />;

    return (
        <Form id="vehicle-form" onSubmit={onSubmit} noValidate>
            <Form.Group controlId="formRegistrationPlate">
                <FormField
                    label="Numer rejestracyjny:"
                    name="registration_plate"
                    required={true}
                    value={vehicle.registration_plate}
                    onChange={handleChanges}
                    errors={errors.registration_plate}
                />
            </Form.Group>
            <Form.Row>
                <Form.Group as={Col} controlId="formBrand" sm="6">
                    <FormField
                        label="Marka:"
                        name="brand"
                        required={true}
                        value={vehicle.brand}
                        onChange={handleChanges}
                        errors={errors.brand}
                    />
                </Form.Group>
                <Form.Group as={Col} controlId="formModel">
                    <FormField
                        label="Model:"
                        name="model"
                        value={vehicle.model}
                        onChange={handleChanges}
                        errors={errors.model}
                    />
                </Form.Group>
            </Form.Row>
            <Form.Row>
                <Form.Group as={Col} controlId="formVolume" sm="6">
                    <FormField
                        label="Pojemność silnika (cm3):"
                        name="engine_volume"
                        type="number"
                        value={vehicle.engine_volume}
                        onChange={handleChanges}
                        errors={errors.engine_volume}
                    />
                </Form.Group>
                <Form.Group as={Col} controlId="formPower">
                    <FormField
                        label="Moc silnika (kW):"
                        name="engine_power"
                        type="number"
                        value={vehicle.engine_power}
                        onChange={handleChanges}
                        errors={errors.engine_power}
                    />
                </Form.Group>
            </Form.Row>
            <Form.Row>
                <Form.Group as={Col} controlId="formYear" sm="6">
                    <FormField
                        label="Rok produkcji:"
                        name="production_year"
                        type="number"
                        value={vehicle.production_year}
                        onChange={handleChanges}
                        errors={errors.production_year}
                    />
                </Form.Group>
                <Form.Group as={Col} controlId="formDate">
                    <FormField
                        label="Data pierwszej rejestracji:"
                        name="registration_date"
                        type="date"
                        value={vehicle.registration_date}
                        onChange={handleChanges}
                        errors={errors.registration_date}
                    />
                </Form.Group>
            </Form.Row>
            <Form.Group controlId="formFuel">
                <FormField
                    label="Rodzaj paliwa:"
                    name="fuel_type"
                    value={vehicle.fuel_type}
                    onChange={handleChanges}
                    errors={errors.fuel_type}
                    type="select"
                    options={FUEL_TYPE}
                />
            </Form.Group>
            <Form.Group controlId="formVIN">
                <FormField label="VIN:" name="vin" value={vehicle.vin} onChange={handleChanges} errors={errors.vin} />
            </Form.Group>
        </Form>
    );
};

VehicleForm.propTypes = {
    vehicleId: PropTypes.string,
    initial: PropTypes.object,
    onSaved: PropTypes.func,
};

export default VehicleForm;
