import React, { useState, useEffect } from "react";

export default function useDebounce(value, delay, callback) {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
        const handler = setTimeout(() => {
            if (value) {
                setDebouncedValue(value);
                callback();
            }
        }, delay);

        return () => {
            clearTimeout(handler);
        };
    }, [value]);

    return debouncedValue;
}
