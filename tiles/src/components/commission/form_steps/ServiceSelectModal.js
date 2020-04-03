import React from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";

import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

import ContentLoading from "../../common/ContentLoading";
import InfiniteSelect from "../../common/InfiniteSelect";

const ServiceSelectModal = ({ show, onHide, onSelect }) => {
    if (!show) return null;
    const SERVICES = gql`
        query getServices($pagination: PageInput, $filters: ServiceFilter) {
            services(pagination: $pagination, filters: $filters) {
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

    const { loading, data, fetchMore, refetch } = useQuery(SERVICES, {
        variables: {
            pagination: { page: 1 },
            filters: { display_as_button: false }
        }
    });

    const loadServices = page => {
        fetchMore({
            variables: {
                pagination: { page: page }
            },
            updateQuery: (prev, { fetchMoreResult }) => {
                if (!fetchMoreResult) return prev;
                return {
                    ...data,
                    services: {
                        ...data.services,
                        pageInfo: {
                            ...fetchMoreResult.services.pageInfo
                        },
                        objects: [...prev.services.objects, ...fetchMoreResult.services.objects]
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
                <Modal show={show} onHide={onHide} size="lg" centered>
                    <Modal.Header closeButton>
                        <Modal.Title>Wybierz usługę</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <InfiniteSelect
                            refetch={value =>
                                refetch({
                                    filters: { display_as_button: false, name__icontains: value.trim() },
                                    pagination: { page: 1 }
                                })
                            }
                            searchPlaceholder="Podaj nazwę usługi"
                            autoFocus={true}
                            show={true}
                            loadMore={loadServices}
                            hasMore={data.services.pageInfo.hasNextPage}
                            objects={data.services.objects}
                            getObjectLabel={service => service.name}
                            onChange={(value, label) => {
                                onSelect(data.services.objects.find(x => x.id === value));
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
    onHide: PropTypes.func.isRequired
};

export default ServiceSelectModal;