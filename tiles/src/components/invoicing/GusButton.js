import React from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useLazyQuery } from "@apollo/react-hooks";

import Button from "react-bootstrap/Button";
import {genericError} from "../../utils";

const GUS_ADDRESS = gql`
    query getGusAddress($nip: String!) {
        gusAddress(nip: $nip) {
            name
            street_address
            postal_code
            city
        }
    }
`;

const GusButton = ({ nip, onCompleted }) => {
    const [getGusAddress, { loading, data }] = useLazyQuery(GUS_ADDRESS, {
        onCompleted: (data) => {
            if(data.gusAddress === null) {
                genericError();
            } else {
                onCompleted(data.gusAddress);
            }
        },
    });

    return (
        <Button
            disabled={nip && nip.length === 10 ? false : true}
            variant="outline-info"
            size="lg"
            onClick={() => getGusAddress({ variables: { nip: nip } })}
        >
            GUS
        </Button>
    );
};

GusButton.propTypes = {
    nip: PropTypes.string,
    onCompleted: PropTypes.func.isRequired,
};

export default GusButton;
