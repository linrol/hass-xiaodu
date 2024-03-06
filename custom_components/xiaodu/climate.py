import logging
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode, FAN_MIDDLE, FAN_HIGH, \
    FAN_MEDIUM, FAN_LOW, SWING_OFF, SWING_VERTICAL, SWING_HORIZONTAL, SWING_BOTH, FAN_OFF, FAN_AUTO
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .coordinator import XiaoDuCoordinator
from .xiaodu import XiaoDuHub

_LOGGER = logging.getLogger(__name__)

# 窗帘
SUPPORT_TYPE = ['AIR_CONDITION']

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry,async_add_entities: AddEntitiesCallback,) -> None:
    coordinator: XiaoDuCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(parse_data(coordinator))


class XiaoDuClimate(ClimateEntity):

    def __init__(self, application_id, appliance_type, name_type, bot_id,bot_name) -> None:
        self._update_value()

        self._appliance_type = appliance_type
        self._attr_unique_id = application_id
        self._attr_name = name_type
        self.bot_id = bot_id
        self.bot_name = bot_name
        self._attr_icon = 'mdi:air-conditioner'

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.AUTO,
            HVACMode.COOL,
            HVACMode.HEAT,
            HVACMode.DRY,
            HVACMode.FAN_ONLY
        ]

        self._attr_fan_modes = [
            FAN_AUTO,
            FAN_LOW,
            FAN_MEDIUM,
            FAN_HIGH
        ]

        self._attr_swing_modes = [
            SWING_OFF,
            SWING_VERTICAL,
            SWING_HORIZONTAL,
            SWING_BOTH
        ]

        self._attr_device_class = "ac"
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE \
                                        | ClimateEntityFeature.FAN_MODE \
                                        | ClimateEntityFeature.SWING_MODE


    def _update_value(self):
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_fan_mode = FAN_OFF
        self._attr_swing_mode = SWING_OFF
        pass

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        pass

    def set_fan_mode(self, fan_mode: str) -> None:
        pass

    def set_swing_mode(self, swing_mode: str) -> None:
        pass

    def set_temperature(self, **kwargs) -> None:
        pass

def parse_data(coordinator: XiaoDuCoordinator) -> list[XiaoDuClimate]:
    appliances = coordinator.data['data']['appliances']
    l: list[XiaoDuClimate] = []
    if len(appliances) > 0:
        for app in appliances:
            appliance_type = app['applianceTypes'][0]
            if appliance_type in SUPPORT_TYPE:
                entity_id = app['applianceId']
                name_type = app['friendlyName']
                bot_id = app['botId']
                bot_name = app['botName']
                l.append(XiaoDuClimate(entity_id, appliance_type, name_type, bot_id, bot_name))
    return l
