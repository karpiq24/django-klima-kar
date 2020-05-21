import React from "react";
import PropTypes from "prop-types";
import { useQuery } from "@apollo/react-hooks";
import { gql } from "apollo-boost";

import Card from "react-bootstrap/Card";
import Table from "react-bootstrap/Table";
import Accordion from "react-bootstrap/Accordion";

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
                phone_1_formatted
                phone_2_formatted
            }
        }
    }
`;

const ContractorCard = ({ id, className, bg, border }) => {
    const { loading, data } = useQuery(CONTRACTOR, {
        fetchPolicy: "no-cache",
        variables: { filters: { id: id } },
    });
    let contractor = null;
    if (!loading) {
        contractor = data.contractors.objects[0];
    }

    return (
        <Card className={className} bg={bg} border={border}>
            {loading || contractor === null ? (
                <ContentLoading />
            ) : (
                <>
                    <Accordion.Toggle as={Card.Header} eventKey="contractor">
                        Kontrahent: {contractor.name}
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="contractor">
                        <Card.Body>
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
                                    {contractor.phone_1_formatted ? (
                                        <tr>
                                            <td>Numer telefonu</td>
                                            <td>{contractor.phone_1_formatted}</td>
                                        </tr>
                                    ) : null}
                                    {contractor.phone_2_formatted ? (
                                        <tr>
                                            <td>Numer telefonu 2</td>
                                            <td>{contractor.phone_2_formatted}</td>
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
                        </Card.Body>
                    </Accordion.Collapse>
                </>
            )}
        </Card>
    );
};

ContractorCard.propTypes = {
    id: PropTypes.string.isRequired,
    className: PropTypes.string,
    bg: PropTypes.string,
    border: PropTypes.string,
};

export default ContractorCard;
