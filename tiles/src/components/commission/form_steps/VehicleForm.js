import React from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useQuery } from "@apollo/react-hooks";

import Form from "react-bootstrap/Form";

import ContentLoading from "../../common/ContentLoading";
import InfiniteSelect from "../../common/InfiniteSelect";

const VehicleForm = ({ currentStep, commission, onChange }) => {
    if (currentStep !== 2) return null;

    const VEHICLES = gql`
        query getVehicles($pagination: PageInput, $filters: VehicleFilter) {
            vehicles(pagination: $pagination, filters: $filters) {
                pageInfo {
                    hasPreviousPage
                    hasNextPage
                    numPages
                    count
                    pageNumber
                }
                objects {
                    id
                    registration_plate
                    brand
                    model
                    production_year
                }
            }
        }
    `;

    const { loading, data, fetchMore, refetch } = useQuery(VEHICLES, {
        variables: {
            pagination: { page: 1 },
            filters: {}
        }
    });

    const loadVehicles = page => {
        fetchMore({
            variables: {
                pagination: { page: page }
            },
            updateQuery: (prev, { fetchMoreResult }) => {
                if (!fetchMoreResult) return prev;
                return {
                    ...data,
                    vehicles: {
                        ...data.vehicles,
                        pageInfo: {
                            ...fetchMoreResult.vehicles.pageInfo
                        },
                        objects: [...prev.vehicles.objects, ...fetchMoreResult.vehicles.objects]
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
                    <h2>Wybierz pojazd:</h2>
                    <InfiniteSelect
                        refetch={value =>
                            refetch({
                                filters: { registration_plate__icontains: value.trim() },
                                pagination: { page: 1 }
                            })
                        }
                        searchPlaceholder="Podaj numer rejestracyjny"
                        createLabel="Dodaj nowy pojazd"
                        autoFocus={true}
                        show={true}
                        loadMore={loadVehicles}
                        hasMore={data.vehicles.pageInfo.hasNextPage}
                        objects={data.vehicles.objects}
                        getObjectLabel={vehicle =>
                            [
                                vehicle.registration_plate,
                                vehicle.brand,
                                vehicle.model,
                                vehicle.production_year ? `(${vehicle.production_year})` : null
                            ]
                                .filter(Boolean)
                                .join(" ")
                        }
                        selected={commission.vehicle}
                        selectedLabel={commission.vc_name}
                        onCreate={(value) => console.log(value)}
                        onChange={(value, label) =>
                            onChange(
                                {
                                    vehicle: value,
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

VehicleForm.propTypes = {
    currentStep: PropTypes.number.isRequired,
    commission: PropTypes.object.isRequired,
    onChange: PropTypes.func.isRequired
};

export default VehicleForm;
