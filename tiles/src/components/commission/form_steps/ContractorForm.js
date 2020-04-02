import React from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";

import Form from "react-bootstrap/Form";

import ContentLoading from "../../common/ContentLoading";
import InfiniteSelect from "../../common/InfiniteSelect";

const ContractorForm = ({ currentStep, commission, onChange }) => {
    if (currentStep !== 3) return null;

    const CONTRACTORS = gql`
        query getContractors($pagination: PageInput, $filters: ContractorFilter) {
            contractors(pagination: $pagination, filters: $filters) {
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
            filters: {}
        }
    });

    const loadContractors = page => {
        fetchMore({
            variables: {
                pagination: { page: page }
            },
            updateQuery: (prev, { fetchMoreResult }) => {
                if (!fetchMoreResult) return prev;
                return {
                    ...data,
                    contractors: {
                        ...data.contractors,
                        pageInfo: {
                            ...fetchMoreResult.contractors.pageInfo
                        },
                        objects: [...prev.contractors.objects, ...fetchMoreResult.contractors.objects]
                    }
                };
            }
        });
    };

    return (
        <>
            {data === undefined ? (
                <ContentLoading />
            ) : (
                <Form.Group>
                    <h2>Wybierz kontrahenta:</h2>
                    <InfiniteSelect
                        refetch={value =>
                            refetch({
                                filters: { name__icontains: value.trim() },
                                pagination: { page: 1 }
                            })
                        }
                        searchPlaceholder="Podaj nazwę"
                        createLabel="Dodaj nowego kontrahenta"
                        autoFocus={true}
                        show={true}
                        loadMore={loadContractors}
                        hasMore={data.contractors.pageInfo.hasNextPage}
                        objects={data.contractors.objects}
                        getObjectLabel={contractor => contractor.name}
                        selected={commission.contractor}
                        selectedLabel={commission.contractorLabel}
                        onChange={(value, label) =>
                            onChange(
                                {
                                    contractor: value,
                                    contractorLabel: label
                                },
                                true
                            )
                        }
                    />
                </Form.Group>
            )}
        </>
    );
};

ContractorForm.propTypes = {
    currentStep: PropTypes.number.isRequired,
    commission: PropTypes.object.isRequired,
    onChange: PropTypes.func.isRequired
};

export default ContractorForm;
