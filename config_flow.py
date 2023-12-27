"""Config flow for Devialet Expert."""

import asyncio
from contextlib import suppress
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_entry_flow
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DISPATCH_CONTROLLER_DISCOVERED, DOMAIN, DEFAULT_SCAN_INTERVAL
from .discovery import async_start_network_controller, async_stop_network_controller

_LOGGER = logging.getLogger(__name__)


async def _async_has_devices(hass: HomeAssistant) -> bool:
    device_ready = asyncio.Event()

    @callback
    def dispatch_discovered(_):
        device_ready.set()

    async_dispatcher_connect(hass, DISPATCH_CONTROLLER_DISCOVERED, dispatch_discovered)

    nc = await async_start_network_controller(hass)

    with suppress(asyncio.TimeoutError):
        async with asyncio.timeout(DEFAULT_SCAN_INTERVAL):
            await device_ready.wait()

    if not nc.get_devices():
        await async_stop_network_controller(hass)
        _LOGGER.info("No devices found")
        return False

    _LOGGER.info("Devialet Devices %s", nc.get_devices())
    return True


config_entry_flow.register_discovery_flow(DOMAIN, "Devialet Expert", _async_has_devices)
