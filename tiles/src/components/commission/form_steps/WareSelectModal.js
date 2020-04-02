import React from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";

import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

import ContentLoading from "../../common/ContentLoading";
import InfiniteSelect from "../../common/InfiniteSelect";

const WareSelectModal = ({ show, onHide, onSelect, wareName }) => {
    if (!show) return null;
    const WARES = gql`
        query getWares($pagination: PageInput, $filters: WareFilter) {
            wares(pagination: $pagination, filters: $filters) {
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
                    index
                    retail_price
                }
            }
        }
    `;

    const { loading, data, fetchMore, refetch } = useQuery(WARES, {
        variables: {
            pagination: { page: 1 },
            filters: { name: wareName }
        }
    });

    const loadWares = page => {
        fetchMore({
            variables: {
                pagination: { page: page }
            },
            updateQuery: (prev, { fetchMoreResult }) => {
                if (!fetchMoreResult) return prev;
                return {
                    ...data,
                    wares: {
                        ...data.wares,
                        pageInfo: {
                            ...fetchMoreResult.wares.pageInfo
                        },
                        objects: [...prev.wares.objects, ...fetchMoreResult.wares.objects]
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
                        <Modal.Title>Wybierz towar</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <InfiniteSelect
                            refetch={value =>
                                refetch({
                                    filters: { name: wareName, index_custom: value.trim() },
                                    pagination: { page: 1 }
                                })
                            }
                            searchPlaceholder="Podaj indeks towaru"
                            autoFocus={true}
                            show={true}
                            loadMore={loadWares}
                            hasMore={data.wares.pageInfo.hasNextPage}
                            objects={data.wares.objects}
                            getObjectLabel={ware => ware.index}
                            onChange={(value, label) => {
                                onSelect(data.wares.objects.find(x => x.id === value));
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

WareSelectModal.propTypes = {
    show: PropTypes.bool.isRequired,
    onSelect: PropTypes.func.isRequired,
    onHide: PropTypes.func.isRequired
};

export default WareSelectModal;
