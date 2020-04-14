import React from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";

import Form from "react-bootstrap/Form";

import ContentLoading from "../../common/ContentLoading";
import InfiniteSelect from "../../common/InfiniteSelect";

const ComponentForm = ({ currentStep, commission, onChange }) => {
    if (currentStep !== 2) return null;

    const COMPONENTS = gql`
        query getComponents($pagination: PageInput, $filters: ComponentFilter) {
            components(pagination: $pagination, filters: $filters) {
                pageInfo {
                    hasPreviousPage
                    hasNextPage
                    numPages
                    count
                    pageNumber
                }
                objects {
                    id
                    component_type
                    get_component_type_display
                    model
                    serial_number
                    catalog_number
                }
            }
        }
    `;

    const { loading, data, fetchMore, refetch } = useQuery(COMPONENTS, {
        variables: {
            pagination: { page: 1 },
            filters: {}
        }
    });

    const loadComponents = page => {
        fetchMore({
            variables: {
                pagination: { page: page }
            },
            updateQuery: (prev, { fetchMoreResult }) => {
                if (!fetchMoreResult) return prev;
                return {
                    ...data,
                    components: {
                        ...data.components,
                        pageInfo: {
                            ...fetchMoreResult.components.pageInfo
                        },
                        objects: [...prev.components.objects, ...fetchMoreResult.components.objects]
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
                    <h2>Wybierz podzespół:</h2>
                    <InfiniteSelect
                        refetch={value =>
                            refetch({
                                filters: { model__icontains: value.trim() },
                                pagination: { page: 1 }
                            })
                        }
                        searchPlaceholder="Podaj model"
                        createLabel="Dodaj nowy podzespół"
                        autoFocus={true}
                        show={true}
                        loadMore={loadComponents}
                        hasMore={data.components.pageInfo.hasNextPage}
                        objects={data.components.objects}
                        getObjectLabel={component =>
                            [
                                component.get_component_type_display,
                                component.model,
                                component.serial_number,
                                component.catalog_number
                            ]
                                .filter(Boolean)
                                .join(" ")
                        }
                        selected={commission.component}
                        selectedLabel={commission.vc_name}
                        onCreate={(value) => console.log(value)}
                        onChange={(value, label) =>
                            onChange(
                                {
                                    component: value,
                                    vc_name: label
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

ComponentForm.propTypes = {
    currentStep: PropTypes.number.isRequired,
    commission: PropTypes.object.isRequired,
    onChange: PropTypes.func.isRequired
};

export default ComponentForm;
