import React from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";

import InfiniteScroll from "react-infinite-scroller";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

import ContentLoading from "../../common/ContentLoading";
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
                    description
                    button_name
                    button_color
                    ware {
                        id
                        index
                        name
                    }
                    quantity
                    price_brutto
                    is_ware_service
                    ware_filter
                    is_group
                }
            }
        }
    `;

    const queryOptions = serviceGroup
        ? {
              variables: {
                  pagination: { page: 1 },
                  filters: { servicetemplate: serviceGroup },
              },
          }
        : {
              variables: {
                  pagination: { page: 1 },
                  filters: { display_as_button: false, servicetemplate: null },
              },
          };

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
                        <InfiniteScroll
                            pageStart={1}
                            loadMore={loadServices}
                            hasMore={data.services.pageInfo.hasNextPage}
                            useWindow={false}
                            loader={<ContentLoading key="loading" />}
                        >
                            <div className="service-button-container">
                                {data.services.objects.map((service) => (
                                    <Button
                                        variant={service.button_color}
                                        size="xxl"
                                        key={service.id}
                                        onClick={() => {
                                            onHide();
                                            onSelect(service);
                                        }}
                                    >
                                        {service.button_name || service.name}
                                    </Button>
                                ))}
                            </div>
                        </InfiniteScroll>
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
