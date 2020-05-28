import React from "react";
import PropTypes from "prop-types";
import moment from "moment";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlusSquare } from "@fortawesome/free-solid-svg-icons/faPlusSquare";
import { faPencilAlt } from "@fortawesome/free-solid-svg-icons/faPencilAlt";

import Card from "react-bootstrap/Card";
import ListGroup from "react-bootstrap/ListGroup";
import Button from "react-bootstrap/Button";

const CommissionNotesCard = (props) => {
    return (
        <Card className={props.className} bg={props.bg} border={props.border}>
            <Card.Header>Notatki</Card.Header>
            <ListGroup>
                {props.notes.length > 0 ? (
                    props.notes.map((note) => (
                        <ListGroup.Item key={note.id} className="d-flex justify-content-between align-items-start">
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
            <Card.Footer>
                <Button size="lg" variant="outline-success" onClick={props.handleCreateModal}>
                    <FontAwesomeIcon icon={faPlusSquare} /> Dodaj nową notatkę
                </Button>
            </Card.Footer>
        </Card>
    );
};

CommissionNotesCard.propTypes = {
    handleEditModal: PropTypes.func,
    handleCreateModal: PropTypes.func,
    notes: PropTypes.array,
    className: PropTypes.string,
    bg: PropTypes.string,
    border: PropTypes.string,
};

export default CommissionNotesCard;
