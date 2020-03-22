import React from "react";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { gql } from "apollo-boost";
import { useLazyQuery } from "@apollo/react-hooks";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import ContentLoading from "../common/ContentLoading";

const CommissionForm = props => {
    const COMMISSION = gql`
        query getCommission($filters: CommissionFilter) {
            commissions(filters: $filters) {
                objects {
                    id
                    vc_name
                    vehicle {
                        id
                    }
                    component {
                        id
                    }
                    commission_type
                    contractor {
                        id
                        name
                    }
                    description
                    start_date
                    end_date
                    value
                    items {
                        name
                        quantity
                        price
                    }
                }
            }
        }
    `;
    const id = props.match.params.id;
    const [getCommission, { loading, data }] = useLazyQuery(COMMISSION, {
        variables: { filters: { id: id } }
    });

    if (loading) return <ContentLoading />;

    if (id !== undefined && data === undefined) {
        getCommission();
    }

    return (
        <>
            <div className="commission-buttons">
                <Link to="/tiles">
                    <Button variant="outline-primary" size="xl">
                        Wróć do zleceń
                    </Button>
                </Link>
            </div>
            <div>
                <h1>{id ? `Edycja zlecenia ${id}` : "Nowe zlecenie"}</h1>
                <Form>
                    <Form.Group controlId="formBasicEmail">
                        <Form.Label>Pojazd</Form.Label>
                        <Form.Control size="lg" placeholder="Podaj numer rejestracyjny" />
                    </Form.Group>

                    <Form.Group controlId="formBasicPassword">
                        <Form.Label>Password</Form.Label>
                        <Form.Control type="password" placeholder="Password" />
                    </Form.Group>
                    <Form.Group controlId="formBasicCheckbox">
                        <Form.Check type="checkbox" label="Check me out" />
                    </Form.Group>
                    <Button variant="primary" type="submit">
                        Submit
                    </Button>
                </Form>
            </div>
        </>
    );
};

CommissionForm.propTypes = {};

export default CommissionForm;
