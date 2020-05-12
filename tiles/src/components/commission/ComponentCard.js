import React from "react";
import PropTypes from "prop-types";
import { useQuery } from "@apollo/react-hooks";
import { gql } from "apollo-boost";

import Table from "react-bootstrap/Table";
import Card from "react-bootstrap/Card";
import Accordion from "react-bootstrap/Accordion";

import ContentLoading from "../common/ContentLoading";

const COMPONENT = gql`
    query getCompoment($filters: ComponentFilter) {
        components(filters: $filters) {
            objects {
                component_type
                get_component_type_display
                model
                serial_number
                catalog_number
            }
        }
    }
`;

const ComponentCard = ({ id, className, bg, border }) => {
    const { loading, data } = useQuery(COMPONENT, {
        variables: { filters: { id: id } },
    });
    let component = null;
    if (!loading) {
        component = data.components.objects[0];
    }

    return (
        <Card className={className} bg={bg} border={border}>
            {loading || component === null ? (
                <ContentLoading />
            ) : (
                <>
                    <Accordion.Toggle as={Card.Header} eventKey="component">
                        Podzespół: {component.get_component_type_display}
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="component">
                        <Card.Body>
                            <Table bordered className="table-row-headers">
                                <tbody>
                                    {component.model ? (
                                        <tr>
                                            <td>Model</td>
                                            <td>{component.model}</td>
                                        </tr>
                                    ) : null}
                                    {component.serial_number ? (
                                        <tr>
                                            <td>Numer seryjny</td>
                                            <td>{component.serial_number}</td>
                                        </tr>
                                    ) : null}
                                    {component.catalog_number ? (
                                        <tr>
                                            <td>Numer katalogowy</td>
                                            <td>{component.catalog_number}</td>
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

ComponentCard.propTypes = {
    id: PropTypes.string.isRequired,
    className: PropTypes.string,
    bg: PropTypes.string,
    border: PropTypes.string,
};

export default ComponentCard;
