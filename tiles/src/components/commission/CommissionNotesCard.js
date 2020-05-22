import React, { useState, useRef } from "react";
import PropTypes from "prop-types";
import { useMutation, useQuery } from "@apollo/react-hooks";
import { gql } from "apollo-boost";
import moment from "moment";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlusSquare, faPencilAlt, faSave } from "@fortawesome/free-solid-svg-icons";

import Card from "react-bootstrap/Card";
import ListGroup from "react-bootstrap/ListGroup";
import Button from "react-bootstrap/Button";

import ContentLoading from "../common/ContentLoading";
import Modal from "react-bootstrap/Modal";
import Form from "react-bootstrap/Form";
import ToggleButton from "react-bootstrap/ToggleButton";
import ToggleButtonGroup from "react-bootstrap/ToggleButtonGroup";

const NOTES = gql`
    query getCommissionNotes($filters: CommissionFilter) {
        commissions(filters: $filters) {
            objects {
                notes {
                    id
                    contents
                    created
                    last_edited
                    is_active
                    was_edited
                }
            }
        }
    }
`;

const ADD_NOTE = gql`
    mutation AddCommissionNote($commission: ID!, $contents: String!) {
        addCommissionNote(commission: $commission, contents: $contents) {
            id
        }
    }
`;

const UPDATE_NOTE = gql`
    mutation UpdateCommissionNote($pk: ID!, $contents: String!, $isActive: Boolean!) {
        updateCommissionNote(pk: $pk, contents: $contents, isActive: $isActive) {
            id
        }
    }
`;

const CommissionNotesCard = ({ id, className, bg, border }) => {
    const { loading, data, refetch } = useQuery(NOTES, {
        fetchPolicy: "no-cache",
        variables: { filters: { id: id } },
    });
    let notes = [];
    if (!loading) {
        notes = data.commissions.objects[0].notes || [];
    }

    const [showNoteModal, setShowNoteModal] = useState(false);
    const [currentNote, setCurrentNote] = useState(false);
    const [isUpdating, setIsUpdating] = useState(false);
    const ref = useRef(null);

    const handleEditModal = (note) => {
        setIsUpdating(true);
        setCurrentNote(note);
        setShowNoteModal(true);
        setTimeout(() => ref.current.focus(), 10);
    };

    const handleCreateModal = (note) => {
        setIsUpdating(false);
        setCurrentNote({
            contents: "",
        });
        setShowNoteModal(true);
        setTimeout(() => ref.current.focus(), 10);
    };

    const handleSubmit = () => {
        if (isUpdating)
            updateNote({
                variables: {
                    pk: currentNote.id,
                    contents: currentNote.contents,
                    isActive: currentNote.is_active,
                },
            });
        else
            addNote({
                variables: {
                    commission: id,
                    contents: currentNote.contents,
                },
            });
        setShowNoteModal(false);
    };

    const [addNote] = useMutation(ADD_NOTE, {
        onCompleted: (data) => {
            refetch({ filters: { id: id } });
        },
    });

    const [updateNote] = useMutation(UPDATE_NOTE, {
        onCompleted: (data) => {
            refetch({ filters: { id: id } });
        },
    });

    return (
        <>
            <Card className={className} bg={bg} border={border}>
                {loading ? (
                    <ContentLoading />
                ) : (
                    <>
                        <Card.Header>Notatki</Card.Header>
                        <ListGroup>
                            {notes.length > 0 ? (
                                notes.map((note) => (
                                    <ListGroup.Item
                                        key={note.id}
                                        className="d-flex justify-content-between align-items-start"
                                    >
                                        <div className={note.is_active ? "" : "not-active"}>
                                            <small className="font-weight-bold">
                                                {moment(note.created).locale("pl").calendar()}
                                                {note.was_edited
                                                    ? ` (edytowano ${moment(note.last_edited).locale("pl").calendar()})`
                                                    : null}
                                            </small>
                                            <div className="commission-note">{note.contents}</div>
                                        </div>
                                        <FontAwesomeIcon
                                            className="commission-note-edit"
                                            icon={faPencilAlt}
                                            onClick={() => handleEditModal(note)}
                                        />
                                    </ListGroup.Item>
                                ))
                            ) : (
                                <ListGroup.Item>Brak notatek.</ListGroup.Item>
                            )}
                        </ListGroup>
                        <Card.Footer>
                            <Button size="lg" variant="outline-success" onClick={handleCreateModal}>
                                <FontAwesomeIcon icon={faPlusSquare} /> Dodaj nową notatkę
                            </Button>
                        </Card.Footer>
                    </>
                )}
            </Card>
            <Modal show={showNoteModal} onHide={() => setShowNoteModal(false)} size="lg" centered>
                <Modal.Header>
                    <Modal.Title>{isUpdating ? "Edycja notatki" : "Nowa notatka"}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form.Group controlId="noteForm.contents">
                        <Form.Control
                            as="textarea"
                            ref={ref}
                            size="lg"
                            rows={5}
                            value={currentNote.contents}
                            onChange={(e) =>
                                setCurrentNote({
                                    ...currentNote,
                                    contents: e.target.value,
                                })
                            }
                        />
                    </Form.Group>
                    {isUpdating ? (
                        <Form.Group controlId="noteForm.isActive" className="d-flex justify-content-center">
                            <ToggleButtonGroup
                                name="isActive"
                                type="radio"
                                value={currentNote.is_active}
                                onChange={(state) => setCurrentNote({ ...currentNote, is_active: state })}
                            >
                                <ToggleButton value={true} variant="outline-primary" size="xl">
                                    Notatka aktywna
                                </ToggleButton>
                                <ToggleButton value={false} variant="outline-primary" size="xl">
                                    Notatka nieaktywna
                                </ToggleButton>
                            </ToggleButtonGroup>
                        </Form.Group>
                    ) : null}
                </Modal.Body>
                <Modal.Footer>
                    <Button size="lg" variant="outline-dark" onClick={() => setShowNoteModal(false)}>
                        Anuluj
                    </Button>
                    <Button size="lg" variant="outline-success" onClick={handleSubmit}>
                        <FontAwesomeIcon icon={faSave} /> Zapisz
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
};

CommissionNotesCard.propTypes = {
    id: PropTypes.string.isRequired,
    className: PropTypes.string,
    bg: PropTypes.string,
    border: PropTypes.string,
};

export default CommissionNotesCard;
