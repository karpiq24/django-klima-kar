import React from "react";
import PropTypes from "prop-types";
import { useQuery } from "@apollo/react-hooks";
import { gql } from "apollo-boost";

import Modal from "react-bootstrap/Modal";
import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import ContentLoading from "../common/ContentLoading";

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
            }
        }
    }
`;

const VehicleModal = ({ id, show, onHide }) => {
    const { loading, data } = useQuery(VEHICLE, {
        variables: { filters: { id: id } }
    });
    let vehicle = null;
    if (!loading) {
        vehicle = data.vehicles.objects[0];
    }

    return (
        <Modal centered show={show} onHide={onHide}>
            {loading || vehicle === null ? (
                <ContentLoading />
            ) : (
                <>
                    <Modal.Header>
                        <Modal.Title>
                            {vehicle.brand} {vehicle.model}
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <Table bordered className="table-row-headers">
                            <tbody>
                                {vehicle.registration_plate ? (
                                    <tr>
                                        <td>Numer rejestracyjny</td>
                                        <td>{vehicle.registration_plate}</td>
                                    </tr>
                                ) : null}
                                {vehicle.vin ? (
                                    <tr>
                                        <td>Numer VIN</td>
                                        <td>{vehicle.vin}</td>
                                    </tr>
                                ) : null}
                                {vehicle.engine_volume ? (
                                    <tr>
                                        <td>Pojemność silnika (cm3)</td>
                                        <td>{vehicle.engine_volume}</td>
                                    </tr>
                                ) : null}
                                {vehicle.engine_power ? (
                                    <tr>
                                        <td>Moc silnika (kW)</td>
                                        <td>{vehicle.engine_power}</td>
                                    </tr>
                                ) : null}
                                {vehicle.production_year ? (
                                    <tr>
                                        <td>Rok produkcji</td>
                                        <td>{vehicle.production_year}</td>
                                    </tr>
                                ) : null}
                            </tbody>
                        </Table>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button size="lg" variant="outline-dark" onClick={onHide}>
                            Zamknij
                        </Button>
                    </Modal.Footer>
                </>
            )}
        </Modal>
    );
};

VehicleModal.propTypes = {
    id: PropTypes.number.isRequired,
    show: PropTypes.bool.isRequired,
    onHide: PropTypes.func.isRequired
};

export default VehicleModal;
