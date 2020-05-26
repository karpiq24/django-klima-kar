import React, { useState } from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";

import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEdit } from "@fortawesome/free-solid-svg-icons";

import ContentLoading from "../../common/ContentLoading";
import InfiniteSelect from "../../common/InfiniteSelect";
import ModalForm from "../../common/ModalForm";
import ContractorForm from "../../invoicing/ContractorForm";
import { isInt } from "../../../utils";
import Alert from "react-bootstrap/Alert";

const ContractorInput = ({ currentStep, commission, onChange, errors }) => {
    if (currentStep !== 3) return null;

    const CONTRACTORS = gql`
        query getContractors($pagination: PageInput, $filters: ContractorFilter, $search: String) {
            contractors(pagination: $pagination, filters: $filters, search: $search) {
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
                }
            }
        }
    `;

    const { loading, data, fetchMore, refetch } = useQuery(CONTRACTORS, {
        variables: {
            pagination: { page: 1 },
            filters: {},
        },
    });

    const [createInitial, setCreateInitial] = useState(null);
    const [showModal, setShowModal] = useState(false);

    const loadContractors = (page) => {
        fetchMore({
            variables: {
                pagination: { page: page },
            },
            updateQuery: (prev, { fetchMoreResult }) => {
                if (!fetchMoreResult) return prev;
                return {
                    ...data,
                    contractors: {
                        ...data.contractors,
                        pageInfo: {
                            ...fetchMoreResult.contractors.pageInfo,
                        },
                        objects: [...prev.contractors.objects, ...fetchMoreResult.contractors.objects],
                    },
                };
            },
        });
    };

    return (
        <>
            {data === undefined ? (
                <ContentLoading />
            ) : (
                <>
                    <div className="error-list">
                        {errors.contractor
                            ? errors.contractor.map((error, idx) => (
                                  <Alert key={idx} variant="danger">
                                      {error}
                                  </Alert>
                              ))
                            : null}
                    </div>
                    <Form.Group>
                        <h2>Wybierz kontrahenta:</h2>
                        <div className="d-flex">
                            <InfiniteSelect
                                refetch={(value) =>
                                    refetch({
                                        search: value.trim(),
                                        pagination: { page: 1 },
                                    })
                                }
                                searchPlaceholder="Podaj nazwę, NIP albo numer telefonu"
                                createLabel="Dodaj nowego kontrahenta"
                                autoFocus={true}
                                show={true}
                                loadMore={loadContractors}
                                hasMore={data.contractors.pageInfo.hasNextPage}
                                objects={data.contractors.objects}
                                getObjectLabel={(contractor) => contractor.name}
                                selected={commission.contractor}
                                selectedLabel={commission.contractorLabel}
                                onCreate={(value) => {
                                    if (isInt(value) && value.length === 9) setCreateInitial({ phone_1: value });
                                    else if (isInt(value)) setCreateInitial({ nip: value });
                                    else setCreateInitial({ name: value });
                                    setShowModal(true);
                                }}
                                onChange={(value, label) =>
                                    onChange(
                                        {
                                            contractor: value,
                                            contractorLabel: label,
                                        },
                                        value ? true : false
                                    )
                                }
                            />
                            {commission.contractor ? (
                                <Button
                                    variant="warning"
                                    size="lg"
                                    className="ml-2 d-flex align-items-center"
                                    onClick={() => setShowModal(true)}
                                >
                                    <FontAwesomeIcon className="mr-2" icon={faEdit} />
                                    Edytuj
                                </Button>
                            ) : null}
                        </div>
                        <ModalForm
                            show={showModal}
                            onHide={() => setShowModal(false)}
                            formId="contractor-form"
                            title={createInitial ? "Dodaj nowego kontrahenta" : "Edycja kontrahenta"}
                        >
                            <ContractorForm
                                contractorId={createInitial ? null : commission.contractor}
                                initial={createInitial}
                                onSaved={(contractor) =>
                                    onChange(
                                        {
                                            contractor: contractor.id,
                                            contractorLabel: contractor.name,
                                        },
                                        true
                                    )
                                }
                            />
                        </ModalForm>
                    </Form.Group>
                </>
            )}
        </>
    );
};

ContractorInput.propTypes = {
    currentStep: PropTypes.number.isRequired,
    commission: PropTypes.object.isRequired,
    onChange: PropTypes.func.isRequired,
};

export default ContractorInput;
