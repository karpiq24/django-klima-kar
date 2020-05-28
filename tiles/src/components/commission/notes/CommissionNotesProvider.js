import React, { useState, useRef } from "react";
import PropTypes from "prop-types";
import { useMutation, useQuery } from "@apollo/react-hooks";
import { gql } from "apollo-boost";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSave } from "@fortawesome/free-solid-svg-icons/faSave";

import Button from "react-bootstrap/Button";

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

const CommissionNotesProvider = (props) => {
    const { loading, data, refetch } = useQuery(NOTES, {
        fetchPolicy: "no-cache",
        variables: { filters: { id: props.id } },
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
                    commission: props.id,
                    contents: currentNote.contents,
                },
            });
        setShowNoteModal(false);
    };

    const [addNote] = useMutation(ADD_NOTE, {
        onCompleted: (data) => {
            refetch({ filters: { id: props.id } });
        },
    });

    const [updateNote] = useMutation(UPDATE_NOTE, {
        onCompleted: (data) => {
            refetch({ filters: { id: props.id } });
        },
    });

    const { children } = props;
    const childrenPropped = React.Children.map(children, (child) =>
        React.cloneElement(child, {
            notes: notes,
            handleEditModal: handleEditModal,
            handleCreateModal: handleCreateModal,
        })
    );

    return (
        <>
            {childrenPropped}
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
                    <Button size="lg" variant="success" onClick={handleSubmit}>
                        <FontAwesomeIcon icon={faSave} /> Zapisz
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
};

CommissionNotesProvider.propTypes = {
    id: PropTypes.string.isRequired,
    className: PropTypes.string,
    children: PropTypes.node.isRequired,
};

export default CommissionNotesProvider;
