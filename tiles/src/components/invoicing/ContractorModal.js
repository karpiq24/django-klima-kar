import React from "react";
import PropTypes from "prop-types";
import { useQuery } from "@apollo/react-hooks";
import { gql } from "apollo-boost";

import Modal from "react-bootstrap/Modal";
import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import ContentLoading from "../common/ContentLoading";

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

const ContractorModal = ({ id, show, onHide }) => {
    const { loading, data } = useQuery(CONTRACTOR, {
        variables: { filters: { id: id } },
    });
    let contractor = null;
    if (!loading) {
        contractor = data.contractors.objects[0];
    }

    return (
        <Modal centered show={show} onHide={onHide}>
            {loading || contractor === null ? (
                <ContentLoading />
            ) : (
                <>
                    <Modal.Header>
                        <Modal.Title>{contractor.name}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <Table bordered className="table-row-headers">
                            <tbody>
                                {contractor.nip ? (
                                    <tr>
                                        <td>NIP</td>
                                        <td>
                                            {contractor.nip_prefix ? `${contractor.nip_prefix} ` : null}
                                            {contractor.nip}
                                        </td>
                                    </tr>
                                ) : null}
                                {contractor.phone_1 ? (
                                    <tr>
                                        <td>Numer telefonu</td>
                                        <td>{contractor.phone_1}</td>
                                    </tr>
                                ) : null}
                                {contractor.phone_2 ? (
                                    <tr>
                                        <td>Numer telefonu 2</td>
                                        <td>{contractor.phone_2}</td>
                                    </tr>
                                ) : null}
                                {contractor.address_1 ? (
                                    <tr>
                                        <td>Adres</td>
                                        <td>{contractor.address_1}</td>
                                    </tr>
                                ) : null}
                                {contractor.address_2 ? (
                                    <tr>
                                        <td>Adres 2</td>
                                        <td>{contractor.address_2}</td>
                                    </tr>
                                ) : null}
                                {contractor.city ? (
                                    <tr>
                                        <td>Miasto</td>
                                        <td>{contractor.city}</td>
                                    </tr>
                                ) : null}
                                {contractor.postal_code ? (
                                    <tr>
                                        <td>Kod pocztowy</td>
                                        <td>{contractor.postal_code}</td>
                                    </tr>
                                ) : null}
                                {contractor.email ? (
                                    <tr>
                                        <td>Adres e-mail</td>
                                        <td>{contractor.email}</td>
                                    </tr>
                                ) : null}
                                {contractor.bdo_number ? (
                                    <tr>
                                        <td>Numer BDO</td>
                                        <td>{contractor.bdo_number}</td>
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

ContractorModal.propTypes = {
    id: PropTypes.number.isRequired,
    show: PropTypes.bool.isRequired,
    onHide: PropTypes.func.isRequired,
};

export default ContractorModal;
