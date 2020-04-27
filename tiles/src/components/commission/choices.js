export const PETROL = "P";
export const DIESEL = "D";
export const MIXED = "M";
export const LPG = "LPG";
export const CNG = "CNG";
export const HYDROGEN = "H";
export const LNG = "LNG";
export const BIODIESEL = "BD";
export const ETHANOL = "E85";
export const ELECTRIC = "EE";
export const PETROL_ELECTRIC = "P EE";
export const FUEL_OTHER = "999";
export const FUEL_TYPE = [
    { key: PETROL, label: "benzyna" },
    { key: DIESEL, label: "olej napędowy" },
    { key: MIXED, label: "mieszanka (paliwo-olej)" },
    { key: LPG, label: "gaz płynny (propan-butan)" },
    { key: CNG, label: "gaz ziemny sprężony (metan)" },
    { key: HYDROGEN, label: "wodór" },
    { key: LNG, label: "gaz ziemny skroplony (metan)" },
    { key: BIODIESEL, label: "biodiesel" },
    { key: ETHANOL, label: "etanol" },
    { key: ELECTRIC, label: "energia elektryczna" },
    { key: PETROL_ELECTRIC, label: "benzyna, energia elektryczna" },
    { key: FUEL_OTHER, label: "inne" },
];

export const COMPRESSOR = "CO";
export const HEATER = "HE";
export const OTHER = "OT";
export const COMPONENT_TYPE = [
    { key: COMPRESSOR, label: "Sprężarka" },
    { key: HEATER, label: "Ogrzewanie postojowe" },
    { key: OTHER, label: "Inny" },
];

export const OPEN = "OP";
export const READY = "RE";
export const DONE = "DO";
export const ON_HOLD = "HO";
export const CANCELLED = "CA";
export const COMMISSION_STATUS = [
    { key: OPEN, label: "Otwarte" },
    { key: READY, label: "Gotowe" },
    { key: DONE, label: "Zamknięte" },
    { key: ON_HOLD, label: "Wstrzymane" },
    { key: CANCELLED, label: "Anulowane" },
];

export const VEHICLE = "VH";
export const COMPONENT = "CO";
export const COMMISSION_TYPE = [
    { key: VEHICLE, label: "Pojazd" },
    { key: COMPONENT, label: "Podzespół" },
];
