import React from "react";
import PropTypes from "prop-types";

import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

import ListGroup from "react-bootstrap/ListGroup";
import moment from "moment";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPencilAlt, faPlusSquare } from "@fortawesome/free-solid-svg-icons";

const CommissionNotesModal = (props) => {
    return (
        <Modal centered show={props.show} onHide={props.onHide} size="xl">
            <>
                <Modal.Header>
                    <Modal.Title>Notatki zlecenia</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <ListGroup>
                        {props.notes.length > 0 ? (
                            props.notes.map((note) => (
                                <ListGroup.Item
                                    key={note.id}
                                    className="d-flex justify-content-between align-items-start"
                                >
                                    <div className={note.is_active ? "" : "not-active"}>
                                        <small className="font-weight-bold">
                                            {moment(note.created).locale("pl").calendar({sameElse: 'D MMMM YYYY HH:mm:ss'})}
                                            {note.was_edited
                                                ? ` (edytowano ${moment(note.last_edited).locale("pl").calendar({sameElse: 'D MMMM YYYY HH:mm:ss'})})`
                                                : null}
                                        </small>
                                        <div className="commission-note">{note.contents}</div>
                                    </div>
                                    <FontAwesomeIcon
                                        className="commission-note-edit"
                                        icon={faPencilAlt}
                                        onClick={() => props.handleEditModal(note)}
                                    />
                                </ListGroup.Item>
                            ))
                        ) : (
                            <ListGroup.Item>Brak notatek.</ListGroup.Item>
                        )}
                    </ListGroup>
                </Modal.Body>
                <Modal.Footer>
                    <Button size="lg" variant="outline-dark" onClick={props.onHide}>
                        Zamknij
                    </Button>
                    <Button size="lg" variant="success" onClick={props.handleCreateModal}>
                        <FontAwesomeIcon icon={faPlusSquare} /> Dodaj nową notatkę
                    </Button>
                </Modal.Footer>
            </>
        </Modal>
    );
};

CommissionNotesModal.propTypes = {
    show: PropTypes.bool.isRequired,
    onHide: PropTypes.func.isRequired,
    handleEditModal: PropTypes.func,
    handleCreateModal: PropTypes.func,
    notes: PropTypes.array,
};

export default CommissionNotesModal;
