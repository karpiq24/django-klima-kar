import subprocess

from apps.commission.models import Vehicle


def decode_aztec_code(code, create=True):
    try:
        output = subprocess.check_output(["./scripts/aztec", code])
        output = output.decode("utf-16", errors="ignore").strip()
    except subprocess.CalledProcessError:
        return None
    values = output.split("|")
    data = {
        "registration_plate": values[7].strip().replace(" ", ""),
        "vin": values[13].strip(),
        "brand": values[8].strip(),
        "model": values[12].strip(),
        "engine_volume": int(values[48].split(",")[0]),
        "engine_power": int(values[49].split(",")[0]),
        "production_year": int(values[56]),
        "fuel_type": str(values[50]).strip(),
        "registration_date": values[51],
    }
    if create:
        vehicle, created = Vehicle.objects.update_or_create(
            registration_plate=data["registration_plate"], defaults=data
        )
    else:
        try:
            vehicle = Vehicle.objects.get(registration_plate=data["registration_plate"])
        except Vehicle.DoesNotExist:
            vehicle = None
    if vehicle:
        data["pk"] = vehicle.pk
        data["label"] = str(vehicle)
        data["url"] = vehicle.get_absolute_url()
    return data


def decode_mpojazd(csv_data, create=True):
    values = csv_data.split(";")
    if len(values) != 17:
        return None
    data = {
        "registration_plate": values[2],
        "vin": values[3].strip(),
        "brand": values[0].strip(),
        "model": values[1].strip(),
        "engine_volume": int(values[5]),
        "engine_power": int(values[6]),
        "production_year": int(values[4]),
    }
    if create:
        vehicle, created = Vehicle.objects.update_or_create(
            registration_plate=data["registration_plate"], defaults=data
        )
    else:
        try:
            vehicle = Vehicle.objects.get(registration_plate=data["registration_plate"])
        except Vehicle.DoesNotExist:
            vehicle = None
    if vehicle:
        data["pk"] = vehicle.pk
        data["label"] = str(vehicle)
        data["url"] = vehicle.get_absolute_url()
    return data
