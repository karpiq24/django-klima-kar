import React from "react";
import PropTypes from "prop-types";
import { useHistory } from "react-router-dom";

import Button from "react-bootstrap/Button";
import Alert from "react-bootstrap/Alert";
import Table from "react-bootstrap/Table";
import Card from "react-bootstrap/Card";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { faUsers } from "@fortawesome/free-solid-svg-icons/faUsers";
import { faCar } from "@fortawesome/free-solid-svg-icons/faCar";
import { faMicrochip } from "@fortawesome/free-solid-svg-icons/faMicrochip";
import { faStickyNote } from "@fortawesome/free-solid-svg-icons/faStickyNote";
import { displayZloty } from "../../utils";

const CommissionCard = ({ commission, openContractorModal, openVehicleModal, openComponentModal, openNotesModal }) => {
    const history = useHistory();
    return (
        <Card
            key={commission.id}
            bg="light"
            border="dark"
            className="commission-card"
            onClick={() => history.push(`/tiles/zlecenia/${commission.id}`)}
        >
            <Card.Header className="d-flex justify-content-between">
                <div>
                    Zlecenie {commission.id}: {commission.vc_name}
                </div>
            </Card.Header>
            <Card.Body>
                <div className="commission-dates">
                    <div>
                        <header>Data przyjęcia</header>
                        <div>{commission.start_date}</div>
                    </div>
                    {commission.end_date ? (
                        <div>
                            <header>Data zamknięcia</header>
                            <div>{commission.end_date}</div>
                        </div>
                    ) : null}
                </div>
                {commission.description ? <Alert variant="primary">{commission.description}</Alert> : ""}
                {commission.items.length > 0 ? (
                    <Table striped bordered hover responsive>
                        <thead>
                            <tr>
                                <th>Nazwa</th>
                                <th>Cena</th>
                            </tr>
                        </thead>
                        <tbody>
                            {commission.items.map((item, idx) => (
                                <tr key={idx}>
                                    <td>{item.name}</td>
                                    <td>{displayZloty(item.quantity * item.price)}</td>
                                </tr>
                            ))}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td>RAZEM:</td>
                                <td>{displayZloty(commission.value)}</td>
                            </tr>
                        </tfoot>
                    </Table>
                ) : null}
            </Card.Body>
            <Card.Footer className="commission-card-footer">
                {commission.contractor ? (
                    <Button
                        variant="primary"
                        size="lg"
                        className="btn-footer"
                        onClick={(e) => {
                            e.stopPropagation();
                            openContractorModal(commission.contractor.id);
                        }}
                    >
                        <FontAwesomeIcon icon={faUsers} />
                        <span>Kontrahent</span>
                    </Button>
                ) : null}
                {commission.vehicle ? (
                    <Button
                        variant="info"
                        size="lg"
                        className="btn-footer"
                        onClick={(e) => {
                            e.stopPropagation();
                            openVehicleModal(commission.vehicle.id);
                        }}
                    >
                        <FontAwesomeIcon icon={faCar} />
                        <span>Pojazd</span>
                    </Button>
                ) : null}
                {commission.component ? (
                    <Button
                        variant="info"
                        size="lg"
                        className="btn-footer"
                        onClick={(e) => {
                            e.stopPropagation();
                            openComponentModal(commission.component.id);
                        }}
                    >
                        <FontAwesomeIcon icon={faMicrochip} />
                        <span>Podzespół</span>
                    </Button>
                ) : null}
                <Button
                    variant={commission.has_notes ? "danger" : "dark"}
                    size="lg"
                    className="btn-footer"
                    onClick={(e) => {
                        e.stopPropagation();
                        openNotesModal(commission);
                    }}
                >
                    <FontAwesomeIcon icon={faStickyNote} />
                    <span>Notatki</span>
                </Button>
            </Card.Footer>
        </Card>
    );
};

CommissionCard.propTypes = {
    commission: PropTypes.object.isRequired,
    openContractorModal: PropTypes.func.isRequired,
    openVehicleModal: PropTypes.func.isRequired,
    openComponentModal: PropTypes.func.isRequired,
    openNotesModal: PropTypes.func.isRequired,
};

export default CommissionCard;
