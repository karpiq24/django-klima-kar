export const displayZloty = value => {
    return `${parseFloat(value)
        .toFixed(2)
        .replace(".", ",")} zł`;
};
