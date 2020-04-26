export const displayZloty = (value) => {
    return `${parseFloat(value).toFixed(2).replace(".", ",")} zł`;
};

export const isInt = (value) => {
    return !isNaN(value) && parseInt(Number(value), 10) == value && !isNaN(parseInt(value, 10));
};
