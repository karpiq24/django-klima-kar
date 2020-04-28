import React from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";

import ContentLoading from "../common/ContentLoading";
import InfiniteSelect from "../common/InfiniteSelect";
import { displayZloty } from "../../utils";

const WareSelect = (props) => {
    const WARES = gql`
        query getWares($pagination: PageInput, $filters: WareFilter, $search: String) {
            wares(pagination: $pagination, filters: $filters, search: $search) {
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
            filters: props.wareName ? { name: props.wareName } : {},
        },
    });

    const loadWares = (page) => {
        fetchMore({
            variables: {
                pagination: { page: page },
            },
            updateQuery: (prev, { fetchMoreResult }) => {
                if (!fetchMoreResult) return prev;
                return {
                    ...data,
                    wares: {
                        ...data.wares,
                        pageInfo: {
                            ...fetchMoreResult.wares.pageInfo,
                        },
                        objects: [...prev.wares.objects, ...fetchMoreResult.wares.objects],
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
                <InfiniteSelect
                    className={props.className}
                    label={props.label}
                    selected={props.selected}
                    selectedLabel={props.selectedLabel}
                    refetch={(value) =>
                        refetch({
                            search: value.trim(),
                            filters: props.wareName ? { name: props.wareName } : null,
                            pagination: { page: 1 },
                        })
                    }
                    selectPlaceholder={props.selectPlaceholder}
                    searchPlaceholder="Podaj indeks towaru"
                    autoFocus={props.autoFocus}
                    show={props.show}
                    loadMore={loadWares}
                    hasMore={data.wares.pageInfo.hasNextPage}
                    objects={data.wares.objects}
                    getObjectLabel={(ware) =>
                        `${ware.index}${ware.retail_price !== null ? ` - ${displayZloty(ware.retail_price)}` : ""}`
                    }
                    onChange={(value, label) => {
                        if (value === null) return null;
                        props.onChange(data.wares.objects.find((x) => x.id === value));
                    }}
                    errors={props.errors}
                />
            )}
        </>
    );
};

WareSelect.propTypes = {
    wareName: PropTypes.string,
    label: PropTypes.string,
    selectPlaceholder: PropTypes.string,
    autoFocus: PropTypes.bool,
    show: PropTypes.bool,
    selected: PropTypes.string,
    selectedLabel: PropTypes.string,
    onChange: PropTypes.func,
    className: PropTypes.string,
    errors: PropTypes.any,
};

export default WareSelect;
