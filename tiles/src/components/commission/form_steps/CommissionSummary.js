import React from "react";
import PropTypes from "prop-types";
import Form from "react-bootstrap/Form";
import Table from "react-bootstrap/Table";
import { displayZloty } from "../../../utils";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import { COMMISSION_STATUS, VEHICLE } from "../choices";

const CommissionSummary = ({ currentStep, commission }) => {
    if (currentStep !== 8) return null;

    return (
        <Form.Group>
            <Row>
                <Col>
                    <Table bordered className="table-row-headers">
                        <tbody>
                            <tr>
                                <td>Typ zlecenia</td>
                                <td>{commission.commission_type === VEHICLE ? "Pojazd" : "Podzespół"}</td>
                            </tr>
                            <tr>
                                <td>Status zlecenia</td>
                                <td>{COMMISSION_STATUS.filter((x) => x.key === commission.status)[0].label}</td>
                            </tr>
                            <tr>
                                <td>{commission.commission_type === VEHICLE ? "Pojazd" : "Podzespół"}</td>
                                <td>{commission.vc_name}</td>
                            </tr>
                            <tr>
                                <td>Kontrahent</td>
                                <td>{commission.contractorLabel}</td>
                            </tr>
                            <tr>
                                <td>Opis</td>
                                <td>{commission.description}</td>
                            </tr>
                            <tr>
                                <td>Data przyjęcia</td>
                                <td>{commission.start_date}</td>
                            </tr>
                            <tr>
                                <td>Data zakończenia</td>
                                <td>{commission.end_date ? commission.end_date : ""}</td>
                            </tr>
                        </tbody>
                    </Table>
                </Col>

                {commission.items.length > 0 ? (
                    <Col>
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
                                            {item.description ? <div className="mt-1">{item.description}</div> : null}
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
                                        {displayZloty(commission.items.reduce((a, b) => a + b.price * b.quantity, 0))}
                                    </td>
                                </tr>
                            </tfoot>
                        </Table>
                    </Col>
                ) : null}
            </Row>
        </Form.Group>
    );
};

CommissionSummary.propTypes = {
    currentStep: PropTypes.number.isRequired,
    commission: PropTypes.object.isRequired,
};

export default CommissionSummary;
