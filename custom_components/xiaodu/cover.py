import logging
from typing import Any

from homeassistant.components.cover import CoverEntity, CoverDeviceClass, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import XiaoDuCoordinator
from .xiaodu import XiaoDuHub

_LOGGER = logging.getLogger(__name__)

# 窗帘
SUPPORT_TYPE = ['CURTAIN']


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: XiaoDuCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(parse_data(coordinator))


class XiaoDuCurtain(CoordinatorEntity, CoverEntity):
    def __init__(self, coordinator, application_id, appliance_type, name_type, current_cover_position, bot_id, bot_name) -> None:
        super().__init__(coordinator)
        self._is_closed = current_cover_position == 100
        self._appliance_type = appliance_type
        self._attr_unique_id = application_id
        self._attr_name = name_type
        self._attr_current_cover_position = current_cover_position
        self.bot_id = bot_id
        self.bot_name = bot_name
        self._attr_icon = 'mdi:curtains'
        if appliance_type == 'CURTAIN':
            self._attr_device_class = CoverDeviceClass.CURTAIN
            self._attr_supported_features = CoverEntityFeature.SET_POSITION

    @property
    def is_closed(self):
        return self._is_closed

    # @callback
    # def _handle_coordinator_update(self) -> None:
    #     appliances = self.coordinator.data['data']["appliances"]
    #     if len(appliances) > 0:
    #         for app in appliances:
    #             if self._attr_unique_id == app['applianceId']:
    #                 self._is_closed = app['stateSetting']['turnOnState']['value'] == 'OFF'
    #     _LOGGER.info("cover is closed: {}".format(self._is_closed))
    #     self.async_write_ha_state()

    def open_cover(self, **kwargs: Any) -> None:
        hub: XiaoDuHub = self.hass.data[DOMAIN]['hub']
        _LOGGER.info("open_cover")
        hub.curtain_toggle(self._attr_unique_id, "TurnOnRequest")
        self._is_closed = False
        self.async_write_ha_state()

    def close_cover(self, **kwargs: Any) -> None:
        hub: XiaoDuHub = self.hass.data[DOMAIN]['hub']
        hub.curtain_toggle(self._attr_unique_id, "TurnOffRequest")
        _LOGGER.info("close_cover")
        self._is_closed = True
        self.async_write_ha_state()

    def stop_cover(self, **kwargs: Any) -> None:
        hub: XiaoDuHub = self.hass.data[DOMAIN]['hub']
        hub.curtain_stop(self.unique_id)
        _LOGGER.info("stop_cover")
        self._is_closed = False
        self.async_write_ha_state()


def parse_data(coordinator: XiaoDuCoordinator) -> list[XiaoDuCurtain]:
    appliances = coordinator.data['data']['appliances']
    l: list[XiaoDuCurtain] = []
    if len(appliances) > 0:
        for app in appliances:
            appliance_type = app['applianceTypes'][0]
            if appliance_type in SUPPORT_TYPE:
                entity_id = app['applianceId']
                name_type = app['friendlyName']
                bot_id = app['botId']
                bot_name = app['botName']
                # 无法获取当前位置
                current_position = 0
                l.append(XiaoDuCurtain(coordinator, entity_id, appliance_type, name_type, current_position, bot_id,
                                       bot_name))
    return l
