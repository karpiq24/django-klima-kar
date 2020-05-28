import Swal from "sweetalert2";

export const displayZloty = (value) => {
    return `${parseFloat(value).toFixed(2).replace(".", ",")} zł`;
};

export const isInt = (value) => {
    return !isNaN(value) && parseInt(Number(value), 10) == value && !isNaN(parseInt(value, 10));
};

export const genericError = () => {
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
};
