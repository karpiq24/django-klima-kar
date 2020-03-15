import React, { useState, useEffect } from "react";
import { useQuery } from "@apollo/react-hooks";
import { gql } from "apollo-boost";
import moment from "moment";

import ToggleButtonGroup from "react-bootstrap/ToggleButtonGroup";
import ToggleButton from "react-bootstrap/ToggleButton";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import Masonry from "react-masonry-css";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft, faArrowRight } from "@fortawesome/free-solid-svg-icons";

import "../../styles/commission.css";
import ContractorModal from "../invoicing/ContractorModal";
import VehicleModal from "../commission/VehicleModal";
import ComponentModal from "../commission/ComponentModal";
import CommissionCard from "./CommissionCard";

const COMISSIONS = gql`
    query getComissions($pagination: PageInput, $filters: CommissionFilter) {
        commissions(pagination: $pagination, filters: $filters) {
            pageInfo {
                hasPreviousPage
                hasNextPage
                numPages
                count
                pageNumber
            }
            objects {
                id
                vc_name
                vehicle {
                    id
                }
                component {
                    id
                }
                commission_type
                contractor {
                    id
                    name
                }
                description
                start_date
                end_date
                value
                items {
                    name
                    quantity
                    price
                }
            }
        }
    }
`;

const CommissionList = props => {
    const pageSize = 25;
    const [status, setStatus] = useState(["OPEN"]);
    const [contractor, setContractor] = useState(null);
    const [vehicle, setVehicle] = useState(null);
    const [component, setComponent] = useState(null);
    const [contractorModalShow, setContractorModalShow] = useState(false);
    const [vehicleModalShow, setVehicleModalShow] = useState(false);
    const [componentModalShow, setComponentModalShow] = useState(false);
    const { loading, data, refetch } = useQuery(COMISSIONS, {
        variables: {
            pagination: { pageSize: pageSize, page: 1 },
            filters: { status: "OPEN" }
        }
    });

    useEffect(() => {
        const interval = setInterval(() => {
            refetch();
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    const breakpointColumnsObj = {
        default: 3,
        1400: 2,
        700: 1
    };

    const handleStatusChange = val => {
        setStatus(val);
        if (val === "DONE") {
            refetch({ filters: { status: val, end_date: moment().format("YYYY-MM-DD") } });
        } else {
            refetch({ filters: { status: val } });
        }
    };

    const handlePageChange = page => {
        refetch({ pagination: { page: page, pageSize: pageSize } });
    };

    const openContractorModal = value => {
        setContractor(Number(value));
        setContractorModalShow(true);
    };

    const openVehicleModal = value => {
        setVehicle(Number(value));
        setVehicleModalShow(true);
    };

    const openComponentModal = value => {
        setComponent(Number(value));
        setComponentModalShow(true);
    };

    return (
        <div>
            {contractor ? (
                <ContractorModal
                    id={contractor}
                    show={contractorModalShow}
                    onHide={() => setContractorModalShow(false)}
                />
            ) : null}
            {vehicle ? (
                <VehicleModal id={vehicle} show={vehicleModalShow} onHide={() => setVehicleModalShow(false)} />
            ) : null}
            {component ? (
                <ComponentModal id={component} show={componentModalShow} onHide={() => setComponentModalShow(false)} />
            ) : null}
            <div className="commission-buttons">
                <ToggleButtonGroup
                    type="radio"
                    name="type"
                    value={status}
                    onChange={handleStatusChange}
                    className="pretty-select"
                >
                    <ToggleButton value={"OPEN"} variant="primary" size="xl" active>
                        OTWARTE
                    </ToggleButton>
                    <ToggleButton value={"READY"} variant="primary" size="xl">
                        GOTOWE
                    </ToggleButton>
                    <ToggleButton value={"DONE"} variant="primary" size="xl">
                        ZAMKNIĘTE DZISIAJ
                    </ToggleButton>
                    <ToggleButton value={"ON_HOLD"} variant="primary" size="xl">
                        WSTRZYMANE
                    </ToggleButton>
                    <ToggleButton value={"CANCELLED"} variant="primary" size="xl">
                        ANULOWANE
                    </ToggleButton>
                </ToggleButtonGroup>
            </div>
            {!loading ? (
                <>
                    <Masonry
                        breakpointCols={breakpointColumnsObj}
                        className="card-container"
                        columnClassName="card-container-column"
                    >
                        {data.commissions.objects.map(commission => (
                            <CommissionCard
                                key={commission.id}
                                commission={commission}
                                openContractorModal={openContractorModal}
                                openVehicleModal={openVehicleModal}
                                openComponentModal={openComponentModal}
                            />
                        ))}
                    </Masonry>
                    {data.commissions.pageInfo.numPages > 1 ? (
                        <div className="pagination">
                            <div>
                                <Button
                                    size="lg"
                                    variant="outline-primary"
                                    disabled={!data.commissions.pageInfo.hasPreviousPage}
                                    onClick={() => handlePageChange(data.commissions.pageInfo.pageNumber - 1)}
                                >
                                    <FontAwesomeIcon icon={faArrowLeft} /> Poprzednia
                                </Button>
                            </div>
                            <div className="pagination-input">
                                <span>Strona</span>
                                <Form.Control size="lg" value={data.commissions.pageInfo.pageNumber} readOnly={true} />
                                <span>z {data.commissions.pageInfo.numPages}</span>
                            </div>
                            <div>
                                <Button
                                    size="lg"
                                    variant="outline-primary"
                                    disabled={!data.commissions.pageInfo.hasNextPage}
                                    onClick={() => handlePageChange(data.commissions.pageInfo.pageNumber + 1)}
                                >
                                    Następna <FontAwesomeIcon icon={faArrowRight} />
                                </Button>
                            </div>
                        </div>
                    ) : null}
                </>
            ) : null}
        </div>
    );
};

export default CommissionList;
