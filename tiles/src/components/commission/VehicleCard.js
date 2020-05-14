import React from "react";
import PropTypes from "prop-types";
import { useQuery } from "@apollo/react-hooks";
import { gql } from "apollo-boost";

import Table from "react-bootstrap/Table";
import Card from "react-bootstrap/Card";
import Accordion from "react-bootstrap/Accordion";

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
                registration_date
                get_fuel_type_display
            }
        }
    }
`;

const VehicleCard = ({ id, className, bg, border }) => {
    const { loading, data } = useQuery(VEHICLE, {
        fetchPolicy: "no-cache",
        variables: { filters: { id: id } },
    });
    let vehicle = null;
    if (!loading) {
        vehicle = data.vehicles.objects[0];
    }

    return (
        <Card className={className} bg={bg} border={border}>
            {loading || vehicle === null ? (
                <ContentLoading />
            ) : (
                <>
                    <Accordion.Toggle as={Card.Header} eventKey="vehicle">
                        Pojazd: {vehicle.brand} {vehicle.model}
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="vehicle">
                        <Card.Body>
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
                                    {vehicle.registration_date ? (
                                        <tr>
                                            <td>Data pierwszej rejestracji</td>
                                            <td>{vehicle.registration_date}</td>
                                        </tr>
                                    ) : null}
                                    {vehicle.get_fuel_type_display ? (
                                        <tr>
                                            <td>Rodzaj paliwa</td>
                                            <td>{vehicle.get_fuel_type_display}</td>
                                        </tr>
                                    ) : null}
                                </tbody>
                            </Table>
                        </Card.Body>
                    </Accordion.Collapse>
                </>
            )}
        </Card>
    );
};

VehicleCard.propTypes = {
    id: PropTypes.string.isRequired,
    className: PropTypes.string,
    bg: PropTypes.string,
    border: PropTypes.string,
};

export default VehicleCard;
