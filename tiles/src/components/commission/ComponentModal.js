import React from "react";
import PropTypes from "prop-types";
import { useQuery } from "@apollo/react-hooks";
import { gql } from "apollo-boost";

import Modal from "react-bootstrap/Modal";
import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

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

const ComponentModal = ({ id, show, onHide }) => {
    const { loading, data } = useQuery(COMPONENT, {
        fetchPolicy: "no-cache",
        variables: { filters: { id: id } },
    });
    let component = null;
    if (!loading) {
        component = data.components.objects[0];
    }

    return (
        <Modal centered show={show} onHide={onHide} size="lg">
            {loading || component === null ? (
                <ContentLoading />
            ) : (
                <>
                    <Modal.Header>
                        <Modal.Title>{component.get_component_type_display}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
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

ComponentModal.propTypes = {
    id: PropTypes.number.isRequired,
    show: PropTypes.bool.isRequired,
    onHide: PropTypes.func.isRequired,
};

export default ComponentModal;
