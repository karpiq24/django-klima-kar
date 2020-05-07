import React from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";

import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

import ContentLoading from "../../common/ContentLoading";
import InfiniteSelect from "../../common/InfiniteSelect";
import { displayZloty } from "../../../utils";

const ServiceSelectModal = ({ show, onHide, onSelect, serviceGroup }) => {
    if (!show) return null;
    const SERVICES = gql`
        query getServices($pagination: PageInput, $filters: ServiceFilter, $search: String) {
            services(pagination: $pagination, filters: $filters, search: $search) {
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
                    quantity
                    price_brutto
                }
            }
        }
    `;

    let queryOptions = {
        variables: {
            pagination: { page: 1 },
            filters: { display_as_button: false },
        },
    };

    if (serviceGroup) queryOptions.variables.filters["servicetemplate"] = serviceGroup;

    const { loading, data, fetchMore, refetch } = useQuery(SERVICES, queryOptions);

    const loadServices = (page) => {
        fetchMore({
            variables: {
                pagination: { page: page },
            },
            updateQuery: (prev, { fetchMoreResult }) => {
                if (!fetchMoreResult) return prev;
                return {
                    ...data,
                    services: {
                        ...data.services,
                        pageInfo: {
                            ...fetchMoreResult.services.pageInfo,
                        },
                        objects: [...prev.services.objects, ...fetchMoreResult.services.objects],
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
                <Modal show={show} onHide={onHide} size="lg" centered>
                    <Modal.Header closeButton>
                        <Modal.Title>Wybierz usługę</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <InfiniteSelect
                            refetch={(value) =>
                                refetch({
                                    search: value.trim(),
                                    filters: { display_as_button: false },
                                    pagination: { page: 1 },
                                })
                            }
                            searchPlaceholder="Podaj nazwę usługi"
                            autoFocus={true}
                            show={true}
                            loadMore={loadServices}
                            hasMore={data.services.pageInfo.hasNextPage}
                            objects={data.services.objects}
                            getObjectLabel={(service) =>
                                `${service.name}${
                                    service.price_brutto !== null ? ` - ${displayZloty(service.price_brutto)}` : ""
                                }`
                            }
                            onChange={(value, label) => {
                                onSelect(data.services.objects.find((x) => x.id === value));
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
            )}
        </>
    );
};

ServiceSelectModal.propTypes = {
    show: PropTypes.bool.isRequired,
    onSelect: PropTypes.func.isRequired,
    onHide: PropTypes.func.isRequired,
    serviceGroup: PropTypes.any,
};

export default ServiceSelectModal;
