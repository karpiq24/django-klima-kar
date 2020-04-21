import React from "react";
import PropTypes from "prop-types";

import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

import WareSelect from "./WareSelect";

const WareSelectModal = ({ show, onHide, onSelect, wareName }) => {
    if (!show) return null;

    return (
        <>
            <Modal show={show} onHide={onHide} size="lg" centered>
                <Modal.Header closeButton>
                    <Modal.Title>Wybierz towar</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <WareSelect
                        wareName={wareName}
                        autoFocus={true}
                        show={true}
                        onChange={(ware) => {
                            onSelect(ware);
                            onHide();
                        }}
                    />
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="outline-dark" onClick={onHide}>
                        Zamknij
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
};

WareSelectModal.propTypes = {
    show: PropTypes.bool.isRequired,
    onSelect: PropTypes.func.isRequired,
    onHide: PropTypes.func.isRequired,
};

export default WareSelectModal;
