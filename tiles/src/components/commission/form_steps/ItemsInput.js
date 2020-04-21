import React, { useState } from "react";
import PropTypes from "prop-types";

import Form from "react-bootstrap/Form";
import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

import { displayZloty } from "../../../utils";
import "../../../styles/big-table.css";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";
import ContentLoading from "../../common/ContentLoading";
import ServiceSelectModal from "./ServiceSelectModal";
import WareSelectModal from "../../warehouse/WareSelectModal";
import WareSelect from "../../warehouse/WareSelect";

const ItemsInput = ({ currentStep, onChange, addItem, removeItem, commission }) => {
    if (currentStep !== 7) return null;

    const SERVICES = gql`
        {
            services(pagination: { pageSize: 100 }, filters: { display_as_button: true }) {
                pageInfo {
                    hasPreviousPage
                    hasNextPage
                    numPages
                    count
                    pageNumber
                }
                objects {
                    id
                    name
                    description
                    ware {
                        id
                        index
                        name
                    }
                    quantity
                    price_brutto
                    is_ware_service
                    ware_filter
                }
            }
        }
    `;

    const { loading, data } = useQuery(SERVICES);
    const [showOtherServices, setShowOtherServices] = useState(false);
    const [wareService, setWareService] = useState(null);
    const [showWareModal, setShowWareModal] = useState(false);
    if (loading) return <ContentLoading />;

    const handleWareService = (service) => {
        setWareService(service);
        setShowWareModal(true);
    };

    return (
        <Form.Group>
            <h2>Wybierz pozycje zlecenia:</h2>
            {commission.items.length > 0 ? (
                <Table striped bordered hover className="big-table">
                    <thead>
                        <tr>
                            <th className="th-ware">Usługa/Towar</th>
                            <th className="th-price">Cena</th>
                            <th className="th-quantity">Ilość</th>
                            <th className="th-sum">Wartość</th>
                            <th className="th-actions">Akcje</th>
                        </tr>
                    </thead>
                    <tbody>
                        {commission.items.map((item, index) => (
                            <tr key={item.id || `new_${index}`}>
                                <td>
                                    <Form.Control
                                        value={item.name}
                                        placeholder="Podaj nazwę"
                                        size="lg"
                                        onChange={(event) => onChange(index, { name: event.target.value })}
                                    />
                                    <Form.Control
                                        className="mt-1"
                                        value={item.description}
                                        placeholder="Podaj opis"
                                        size="lg"
                                        onChange={(event) => onChange(index, { description: event.target.value })}
                                    />
                                    <WareSelect
                                        className="mt-1"
                                        selectPlaceholder="Wybierz towar"
                                        selected={item.ware}
                                        selectedLabel={item.wareLabel}
                                        onChange={(ware) => onChange(index, { ware: ware.id, wareLabel: ware.index })}
                                    />
                                </td>
                                <td>
                                    <div className="d-flex align-items-center">
                                        <Form.Control
                                            type="number"
                                            step="0.01"
                                            value={item.price}
                                            size="lg"
                                            onChange={(event) => onChange(index, { price: event.target.value })}
                                        />
                                        <span className="ml-2">zł</span>
                                    </div>
                                </td>
                                <td>
                                    <Form.Control
                                        type="number"
                                        value={item.quantity}
                                        size="lg"
                                        onChange={(event) => onChange(index, { quantity: event.target.value })}
                                    />
                                </td>
                                <td>{displayZloty(item.price * item.quantity)}</td>
                                <td>
                                    <FontAwesomeIcon
                                        icon={faTimes}
                                        size="2x"
                                        color="#ff0000"
                                        cursor="pointer"
                                        onClick={() => removeItem(index)}
                                    />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan={3}>Razem:</td>
                            <td colSpan={2}>
                                {displayZloty(commission.items.reduce((a, b) => a + b.price * b.quantity, 0))}
                            </td>
                        </tr>
                    </tfoot>
                </Table>
            ) : null}
            <div className="mb-2 service-button-container">
                {data.services.objects.map((service) => {
                    if (service.is_ware_service) {
                        return (
                            <Button key={service.id} size="xxl mr-2" onClick={() => handleWareService(service)}>
                                {service.name}
                            </Button>
                        );
                    }
                    return (
                        <Button
                            key={service.id}
                            size="xxl mr-2"
                            onClick={() =>
                                addItem({
                                    name: service.name,
                                    price: service.price_brutto || "",
                                    quantity: service.quantity || 1,
                                    description: service.description || "",
                                    ware: service.ware || "",
                                })
                            }
                        >
                            {service.name}
                        </Button>
                    );
                })}
                <Button size="xxl mr-2" onClick={() => setShowOtherServices(true)}>
                    Inne usługi
                </Button>
                <ServiceSelectModal
                    show={showOtherServices}
                    onHide={() => setShowOtherServices(false)}
                    onSelect={(service) =>
                        addItem({
                            name: service.name || "",
                            price: service.price_brutto || "",
                            quantity: service.quantity || 1,
                            description: service.description || "",
                            ware: service.ware ? service.ware.id : null,
                            wareLabel: service.ware ? service.ware.index : null,
                        })
                    }
                />
                {wareService ? (
                    <WareSelectModal
                        show={showWareModal}
                        wareName={wareService.ware_filter}
                        onHide={() => setShowWareModal(false)}
                        onSelect={(ware) =>
                            addItem({
                                name: wareService.name || "",
                                price: ware.retail_price || "",
                                quantity: wareService.quantity || 1,
                                description: wareService.description || "",
                                ware: ware.id,
                                wareLabel: ware.index,
                            })
                        }
                    />
                ) : null}
            </div>
        </Form.Group>
    );
};

ItemsInput.propTypes = {
    currentStep: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
    addItem: PropTypes.func.isRequired,
    commission: PropTypes.object.isRequired,
    removeItem: PropTypes.func.isRequired,
};

export default ItemsInput;
