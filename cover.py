import logging
from typing import Any

from homeassistant.components.cover import CoverEntity, CoverDeviceClass, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
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


class XiaoDuCurtain(CoverEntity):

    def open_cover(self, **kwargs: Any) -> None:
        hub: XiaoDuHub = self.hass.data[DOMAIN]['hub']
        hub.curtain_set_position(self._attr_unique_id, 100)

    def close_cover(self, **kwargs: Any) -> None:
        hub: XiaoDuHub = self.hass.data[DOMAIN]['hub']
        hub.curtain_set_position(self._attr_unique_id, 0)

    def set_cover_position(self, **kwargs: Any) -> None:
        hub: XiaoDuHub = self.hass.data[DOMAIN]['hub']
        position = 8
        hub.curtain_set_position(self._attr_unique_id, position)

    def stop_cover(self, **kwargs: Any) -> None:
        hub: XiaoDuHub = self.hass.data[DOMAIN]['hub']
        hub.curtain_stop(self.unique_id)

    # async def async_open_cover(self, **kwargs: Any) -> None:
    #     await self.hass.async_add_executor_job(self.open_cover)
    #
    # async def async_close_cover(self, **kwargs: Any) -> None:
    #     await self.hass.async_add_executor_job(self.close_cover)
    #
    # async def async_set_cover_position(self, **kwargs: Any) -> None:
    #     await self.hass.async_add_executor_job(self.close_cover, kwargs)
    #
    # async def async_stop_cover(self, **kwargs: Any) -> None:
    #     await self.hass.async_add_executor_job(self.stop_cover, kwargs)

    def __init__(self, application_id, appliance_type, name_type, current_cover_position, bot_id,
                 bot_name) -> None:
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
        self._attr_is_closed = current_cover_position == 100


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
                current_position = 50
                l.append(XiaoDuCurtain(entity_id, appliance_type, name_type, current_position, bot_id,
                                       bot_name))
    return l
