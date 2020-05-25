import React from "react";
import PropTypes from "prop-types";

import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSave } from "@fortawesome/free-solid-svg-icons";

const ModalForm = (props) => {
    return (
        <Modal show={props.show} onHide={props.onHide} size="xl" centered>
            <Modal.Header closeButton>
                <Modal.Title>{props.title}</Modal.Title>
            </Modal.Header>
            <Modal.Body>{props.children}</Modal.Body>
            <Modal.Footer>
                <Button variant="outline-dark" size="lg" onClick={props.onHide}>
                    Zamknij
                </Button>
                <Button variant="outline-primary" size="lg" type="submit" form={props.formId}>
                    <FontAwesomeIcon icon={faSave} /> Zapisz
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

ModalForm.propTypes = {
    children: PropTypes.node.isRequired,
    show: PropTypes.bool.isRequired,
    onHide: PropTypes.func.isRequired,
    formId: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
};

export default ModalForm;
