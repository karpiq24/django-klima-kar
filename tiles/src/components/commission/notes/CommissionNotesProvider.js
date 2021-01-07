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
    query getAnnotations($pagination: PageInput, $filters: AnnotationFilter) {
        annotations(pagination: $pagination, filters: $filters) {
            objects {
                id
                contents
                created
                last_edited
                is_active
                was_edited
            }
        }
    }
`;

const ADD_NOTE = gql`
    mutation AddAnnotation($app_name: String!, $model_name: String!, $object_id: ID!, $contents: String!) {
        addAnnotation(app_name: $app_name, model_name: $model_name, object_id: $object_id, contents: $contents) {
            id
        }
    }
`;

const UPDATE_NOTE = gql`
    mutation UpdateAnnotation($pk: ID!, $contents: String!, $is_active: Boolean!) {
        updateAnnotation(pk: $pk, contents: $contents, is_active: $is_active) {
            id
        }
    }
`;

const CommissionNotesProvider = (props) => {
    const { loading, data, refetch } = useQuery(NOTES, {
        fetchPolicy: "no-cache",
        variables: {
            filters: { object_id: props.id, content_type__app_label: "commission", content_type__model: "commission" },
        },
    });
    let notes = [];
    if (!loading) {
        notes = data.annotations.objects || [];
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
                    is_active: currentNote.is_active,
                },
            });
        else
            addNote({
                variables: {
                    app_name: "commission",
                    model_name: "commission",
                    object_id: props.id,
                    contents: currentNote.contents,
                },
            });
        setShowNoteModal(false);
    };

    const [addNote] = useMutation(ADD_NOTE, {
        onCompleted: (data) => {
            refetch({
                filters: {
                    object_id: props.id,
                    content_type__app_label: "commission",
                    content_type__model: "commission",
                },
            });
        },
    });

    const [updateNote] = useMutation(UPDATE_NOTE, {
        onCompleted: (data) => {
            refetch({
                filters: {
                    object_id: props.id,
                    content_type__app_label: "commission",
                    content_type__model: "commission",
                },
            });
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
