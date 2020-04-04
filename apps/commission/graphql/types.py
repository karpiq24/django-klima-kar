import enum

from ariadne import ObjectType, EnumType, QueryType, MutationType

from apps.commission.models import Commission, Component, Vehicle


commission = ObjectType("Commission")
vehicle = ObjectType("Vehicle")
component = ObjectType("Component")
query = QueryType()
mutation = MutationType()


class CommissionStatus(enum.Enum):
    OPEN = Commission.OPEN
    READY = Commission.READY
    DONE = Commission.DONE
    CANCELLED = Commission.CANCELLED
    ON_HOLD = Commission.ON_HOLD


class CommissionType(enum.Enum):
    VEHICLE = Commission.VEHICLE
    COMPONENT = Commission.COMPONENT


class ComponentType(enum.Enum):
    COMPRESSOR = Component.COMPRESSOR
    HEATER = Component.HEATER
    OTHER = Component.OTHER


class FuelType(enum.Enum):
    PETROL = Vehicle.PETROL
    DIESEL = Vehicle.DIESEL
    MIXED = Vehicle.MIXED
    LPG = Vehicle.LPG
    CNG = Vehicle.CNG
    HYDROGEN = Vehicle.HYDROGEN
    LNG = Vehicle.LNG
    BIODIESEL = Vehicle.BIODIESEL
    ETHANOL = Vehicle.ETHANOL
    ELECTRIC = Vehicle.ELECTRIC
    OTHER = Vehicle.OTHER


commission_status = EnumType("CommissionStatus", CommissionStatus)
commission_type = EnumType("CommissionType", CommissionType)
component_type = EnumType("ComponentType", ComponentType)
fuel_type = EnumType("FuelType", FuelType)
