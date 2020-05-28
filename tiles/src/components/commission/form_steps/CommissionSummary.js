import React from "react";
import PropTypes from "prop-types";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faExclamationCircle } from "@fortawesome/free-solid-svg-icons/faExclamationCircle";

import Table from "react-bootstrap/Table";
import Card from "react-bootstrap/Card";
import Accordion from "react-bootstrap/Accordion";
import Alert from "react-bootstrap/Alert";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

import VehicleCard from "../VehicleCard";
import ContractorCard from "../../invoicing/ContractorCard";
import ComponentCard from "../ComponentCard";
import { displayZloty } from "../../../utils";
import StatusButtons from "./StatusButtons";
import { COMPONENT, VEHICLE } from "../choices";
import CommissionNotesCard from "../notes/CommissionNotesCard";
import CommissionNotesProvider from "../notes/CommissionNotesProvider";

const CommissionSummary = ({ currentStep, commission, onChange }) => {
    if (currentStep !== 8) return null;

    return (
        <>
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div className="text-left">
                    <header className="font-weight-bold">Data przyjęcia</header>
                    <div>{commission.start_date}</div>
                </div>
                <StatusButtons commission={commission} onChange={onChange} size="xl" />
                <div className="text-right">
                    <header className="font-weight-bold">Data zamknięcia</header>
                    <div>{commission.end_date ? commission.end_date : "—"}</div>
                </div>
            </div>

            <Row>
                <Col lg={12} xl={7}>
                    <Accordion className="mb-4" defaultActiveKey="items">
                        {commission.commission_type === VEHICLE ? (
                            commission.vehicle ? (
                                <VehicleCard id={commission.vehicle} bg="light" border="primary" />
                            ) : (
                                <Card bg="light" border="dark">
                                    <Card.Header>Nie wybrano pojazu.</Card.Header>
                                </Card>
                            )
                        ) : null}
                        {commission.commission_type === COMPONENT ? (
                            commission.component ? (
                                <ComponentCard id={commission.component} bg="light" border="primary" />
                            ) : (
                                <Card bg="light" border="dark">
                                    <Card.Header>Nie wybrano podzespołu.</Card.Header>
                                </Card>
                            )
                        ) : null}
                        {commission.contractor ? (
                            <ContractorCard id={commission.contractor} bg="light" border="primary" />
                        ) : (
                            <Card bg="light" border="dark">
                                <Card.Header>Nie wybrano kontrahenta.</Card.Header>
                            </Card>
                        )}
                        {commission.items.length > 0 ? (
                            <Card bg="light" border="primary">
                                <Accordion.Toggle as={Card.Header} eventKey="items">
                                    Pozycje
                                </Accordion.Toggle>
                                <Accordion.Collapse eventKey="items">
                                    <Card.Body>
                                        <Table striped bordered hover responsive>
                                            <thead>
                                                <tr>
                                                    <th className="th-ware">Usługa/Towar</th>
                                                    <th className="th-price">Cena</th>
                                                    <th className="th-quantity">Ilość</th>
                                                    <th className="th-sum">Wartość</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {commission.items.map((item, index) => (
                                                    <tr key={item.id || `new_${index}`}>
                                                        <td>
                                                            <div>{item.name}</div>
                                                            {item.description ? (
                                                                <>
                                                                    <hr />
                                                                    <div>{item.description}</div>
                                                                </>
                                                            ) : null}
                                                        </td>
                                                        <td>{displayZloty(item.price)}</td>
                                                        <td>{item.quantity}</td>
                                                        <td>{displayZloty(item.price * item.quantity)}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                            <tfoot>
                                                <tr>
                                                    <td colSpan={3}>Razem:</td>
                                                    <td>
                                                        {displayZloty(
                                                            commission.items.reduce(
                                                                (a, b) => a + b.price * b.quantity,
                                                                0
                                                            )
                                                        )}
                                                    </td>
                                                </tr>
                                            </tfoot>
                                        </Table>
                                    </Card.Body>
                                </Accordion.Collapse>
                            </Card>
                        ) : (
                            <Card bg="light" border="warning">
                                <Card.Header>Nie wybrano pozycji.</Card.Header>
                            </Card>
                        )}
                    </Accordion>
                </Col>
                <Col>
                    {commission.description ? (
                        <Alert className="detail-description-alert" variant="primary">
                            <div className="d-flex align-items-center">
                                <FontAwesomeIcon icon={faExclamationCircle} size="3x" className="mr-2" />
                                {commission.description}
                            </div>
                        </Alert>
                    ) : null}
                    {commission.id ? (
                        <CommissionNotesProvider id={commission.id}>
                            <CommissionNotesCard border="dark" bg="light" />
                        </CommissionNotesProvider>
                    ) : null}
                </Col>
            </Row>
        </>
    );
};

CommissionSummary.propTypes = {
    currentStep: PropTypes.number.isRequired,
    commission: PropTypes.object.isRequired,
};

export default CommissionSummary;
