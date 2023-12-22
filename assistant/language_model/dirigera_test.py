from dotenv import load_dotenv
import dirigera
from dirigera.devices.light import Light
import os

load_dotenv()

hub = dirigera.Hub(
    token=os.getenv(DIRIGERA_TOKEN),
    ip_address=os.getenv(DIRIGERA_IP)
)

def get_lights_matching_name(hub: dirigera.Hub, name: str) -> list[Light]:
    """Get all lights in room"""
    name = name.lower()
    return [
        light for light in hub.get_lights()
        if light.room.name.lower() == name
        or any(device_set["name"].lower() == name for device_set in light.device_set)
        or light.attributes.custom_name.lower() == name
    ]


lights = get_lights_matching_name(hub, "hallway")

for light in lights:
    light.set_light(lamp_on=True)