import React, { useState } from "react";
import PropTypes from "prop-types";

import Form from "react-bootstrap/Form";
import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes, faPlusSquare } from "@fortawesome/free-solid-svg-icons";

import { displayZloty } from "../../../utils";
import "../../../styles/big-table.css";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";
import ContentLoading from "../../common/ContentLoading";
import ServiceSelectModal from "./ServiceSelectModal";
import WareSelectModal from "../../warehouse/WareSelectModal";
import WareSelect from "../../warehouse/WareSelect";
import FormField from "../../common/FormField";

const ItemsInput = ({ currentStep, onChange, addItem, removeItem, commission, errors }) => {
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
                    button_name
                    button_color
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
            <Row>
                <Col lg="12" xl="7">
                    <Table striped bordered hover className="big-table">
                        <thead>
                            <tr>
                                <th className="th-ware">Usługa/Towar</th>
                                <th className="th-price">Cena</th>
                                <th className="th-quantity">Ilość</th>
                                <th className="th-sum">Wartość</th>
                                <th className="th-actions">
                                    <FontAwesomeIcon icon={faTimes} size="lg" />
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {commission.items.length === 0 ? (
                                <tr>
                                    <td colSpan="5">Brak pozycji</td>
                                </tr>
                            ) : null}
                            {commission.items.map((item, index) => {
                                const hasError = errors.items !== undefined && errors.items[index] !== undefined;
                                return (
                                    <tr key={item.id || `new_${index}`}>
                                        <td>
                                            <FormField
                                                name="name"
                                                placeholder="Podaj nazwę"
                                                required={true}
                                                value={item.name}
                                                onChange={(event) => onChange(index, { name: event.target.value })}
                                                errors={hasError ? errors.items[index].name : []}
                                            />
                                            <FormField
                                                className="mt-1"
                                                name="description"
                                                placeholder="Podaj opis"
                                                value={item.description}
                                                onChange={(event) =>
                                                    onChange(index, { description: event.target.value })
                                                }
                                                errors={hasError ? errors.items[index].description : []}
                                            />
                                            {item.ware ? (
                                                <WareSelect
                                                    className="mt-1"
                                                    errors={hasError ? errors.items[index].ware : undefined}
                                                    selectPlaceholder="Wybierz towar"
                                                    selected={item.ware}
                                                    selectedLabel={item.wareLabel}
                                                    onChange={(ware) =>
                                                        onChange(index, { ware: ware.id, wareLabel: ware.index })
                                                    }
                                                />
                                            ) : null}
                                        </td>
                                        <td>
                                            <div className="d-flex align-items-center">
                                                <FormField
                                                    name="price"
                                                    type="number"
                                                    step="0.01"
                                                    value={item.price}
                                                    onChange={(e) =>
                                                        onChange(index, {
                                                            price:
                                                                e.target.value !== "" ? Number(e.target.value) : null,
                                                        })
                                                    }
                                                    errors={hasError ? errors.items[index].price : []}
                                                />
                                                <span className="ml-2">zł</span>
                                            </div>
                                        </td>
                                        <td>
                                            <FormField
                                                name="quantity"
                                                type="number"
                                                value={item.quantity}
                                                onChange={(e) =>
                                                    onChange(index, {
                                                        quantity: e.target.value !== "" ? Number(e.target.value) : null,
                                                    })
                                                }
                                                errors={hasError ? errors.items[index].quantity : []}
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
                                );
                            })}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td className="text-left border-right-0">
                                    <Button
                                        size="lg"
                                        variant="outline-success"
                                        onClick={() =>
                                            addItem({
                                                name: null,
                                                price: null,
                                                quantity: 1,
                                                description: null,
                                                ware: null,
                                            })
                                        }
                                    >
                                        <FontAwesomeIcon icon={faPlusSquare} size="lg" /> Dodaj pozycję
                                    </Button>
                                </td>
                                <td colSpan={2} className="text-right font-weight-bold border-left-0 border-right-0">
                                    Razem:
                                </td>
                                <td colSpan={2} className="border-left-0">
                                    {displayZloty(commission.items.reduce((a, b) => a + b.price * b.quantity, 0))}
                                </td>
                            </tr>
                        </tfoot>
                    </Table>
                </Col>

                <Col lg="12" xl="5">
                    <div className="mb-2 service-button-container">
                        {data.services.objects.map((service) => {
                            if (service.is_ware_service) {
                                return (
                                    <Button
                                        variant={service.button_color}
                                        key={service.id}
                                        size="xxl"
                                        onClick={() => handleWareService(service)}
                                    >
                                        {service.button_name || service.name}
                                    </Button>
                                );
                            }
                            return (
                                <Button
                                    key={service.id}
                                    variant={service.button_color}
                                    size="xxl"
                                    onClick={() =>
                                        addItem({
                                            name: service.name,
                                            price: service.price_brutto,
                                            quantity: service.quantity || 1,
                                            description: service.description,
                                            ware: service.ware ? service.ware.id : null,
                                            wareLabel: service.ware ? service.ware.index : null,
                                        })
                                    }
                                >
                                    {service.button_name || service.name}
                                </Button>
                            );
                        })}
                        <Button size="xxl" variant="info" onClick={() => setShowOtherServices(true)}>
                            Inne usługi
                        </Button>
                        <ServiceSelectModal
                            show={showOtherServices}
                            onHide={() => setShowOtherServices(false)}
                            onSelect={(service) =>
                                addItem({
                                    name: service.name,
                                    price: service.price_brutto,
                                    quantity: service.quantity || 1,
                                    description: service.description,
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
                                        name: wareService.name,
                                        price: ware.retail_price,
                                        quantity: wareService.quantity || 1,
                                        description: wareService.description,
                                        ware: ware.id,
                                        wareLabel: ware.index,
                                    })
                                }
                            />
                        ) : null}
                    </div>
                </Col>
            </Row>
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
