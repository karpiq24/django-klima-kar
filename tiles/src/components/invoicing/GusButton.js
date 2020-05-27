import React from "react";
import PropTypes from "prop-types";
import { gql } from "apollo-boost";
import { useLazyQuery } from "@apollo/react-hooks";

import Button from "react-bootstrap/Button";
import Swal from "sweetalert2";

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
                Swal.fire({
                    icon: "error",
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 5000,
                    timerProgressBar: true,
                    title: "Błąd!",
                    text: "Coś poszło nie tak. Spróbuj ponownie.",
                    toast: true,
                });
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
