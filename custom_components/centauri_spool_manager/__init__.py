"""Centauri Carbon Spool Manager Integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Centauri Spool Manager component from YAML configuration."""
    _LOGGER.info("Centauri Carbon Spool Manager: Integration loaded")

    # Store integration directory path
    integration = await async_get_integration(hass, DOMAIN)
    integration_dir = Path(integration.file_path).parent

    hass.data[DOMAIN] = {
        "integration_dir": integration_dir,
        "packages_dir": integration_dir / "packages",
        "dashboards_dir": integration_dir / "dashboards",
    }

    _LOGGER.info(f"Integration directory: {integration_dir}")
    _LOGGER.info(f"Packages directory: {integration_dir / 'packages'}")
    _LOGGER.info(f"Dashboards directory: {integration_dir / 'dashboards'}")

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    _LOGGER.info("Centauri Carbon Spool Manager: Setting up from config entry")

    # Get integration paths
    data = hass.data.get(DOMAIN, {})
    packages_dir = data.get("packages_dir")

    if packages_dir and packages_dir.exists():
        _LOGGER.info(f"Packages are available at: {packages_dir}")
        _LOGGER.info("Add this to your configuration.yaml:")
        _LOGGER.info(f"  homeassistant:")
        _LOGGER.info(f"    packages: !include_dir_merge_named {packages_dir}")
    else:
        _LOGGER.warning("Packages directory not found")

    # Store config entry
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["entry"] = entry

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Centauri Carbon Spool Manager: Unloading")

    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop("entry", None)

    return True
