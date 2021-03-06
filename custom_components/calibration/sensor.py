"""Support for calibration sensor."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_ATTRIBUTE,
    CONF_DEVICE_CLASS,
    CONF_NAME,
    CONF_SOURCE,
    CONF_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.helpers import entity_registry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import RegistryEntry, RegistryEntryHider
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, EventType

from .const import (
    ATTR_COEFFICIENTS,
    ATTR_SOURCE,
    ATTR_SOURCE_ATTRIBUTE,
    ATTR_SOURCE_VALUE,
    CONF_CALIBRATION,
    CONF_HIDE_SOURCE,
    CONF_POLYNOMIAL,
    CONF_PRECISION,
    DATA_CALIBRATION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(  # pylint: disable=too-many-locals
    hass: HomeAssistant,
    config: ConfigType,  # pylint: disable=unused-argument
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Calibration sensor."""
    if discovery_info is None:
        return

    calibration = discovery_info[CONF_CALIBRATION]
    conf = hass.data[DATA_CALIBRATION][calibration]

    unique_id = f"{DOMAIN}.{calibration}"
    name = conf.get(CONF_NAME) or calibration.replace("_", " ").title()
    source = conf[CONF_SOURCE]

    unit_of_measurement = conf.get(CONF_UNIT_OF_MEASUREMENT)
    device_class = conf.get(CONF_DEVICE_CLASS)

    ent_reg = entity_registry.async_get(hass)
    source_entity: RegistryEntry | None = ent_reg.async_get(source)
    source_state: State | None = hass.states.get(source)

    if not (attribute := conf.get(CONF_ATTRIBUTE)):

        def get_value(attr: str):
            if source_state and (unit := source_state.attributes.get(attr)):
                return unit
            if source_entity and (unit := getattr(source_entity, attr)):
                return unit
            return None

        unit_of_measurement = unit_of_measurement or get_value(ATTR_UNIT_OF_MEASUREMENT)
        device_class = device_class or get_value(ATTR_DEVICE_CLASS)

    if conf.get(CONF_HIDE_SOURCE) and source_entity and not source_entity.hidden:
        ent_reg.async_update_entity(source, hidden_by=RegistryEntryHider.INTEGRATION)

    async_add_entities(
        [
            CalibrationSensor(
                unique_id,
                name,
                source,
                attribute,
                conf[CONF_PRECISION],
                conf[CONF_POLYNOMIAL],
                unit_of_measurement,
                device_class,
            )
        ]
    )


class CalibrationSensor(SensorEntity):  # pylint: disable=too-many-instance-attributes
    """Representation of a Calibration sensor."""

    def __init__(
        self,
        unique_id: str,
        name: str,
        source: str,
        attribute: str | None,
        precision: int,
        polynomial,
        unit_of_measurement: str | None,
        device_class: str | None,
    ) -> None:
        """Initialize the Calibration sensor."""
        self._source_entity_id = source
        self._source_attribute = attribute
        self._precision = precision
        self._poly = polynomial

        self._attr_unique_id = unique_id
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_device_class = device_class
        self._attr_icon = None
        self._attr_should_poll = False

        attrs = {
            ATTR_SOURCE_VALUE: None,
            ATTR_SOURCE: source,
            ATTR_SOURCE_ATTRIBUTE: attribute,
            ATTR_COEFFICIENTS: polynomial.coef.tolist(),
        }
        self._attr_extra_state_attributes = {
            k: v for k, v in attrs.items() if v or k == ATTR_SOURCE_VALUE
        }

    async def async_added_to_hass(self) -> None:
        """Handle added to Hass."""
        if (state := self.hass.states.get(self._source_entity_id)) is not None:
            self._update_state(state)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._source_entity_id],
                self._async_calibration_sensor_state_listener,
            )
        )

    @callback
    def _async_calibration_sensor_state_listener(self, event: EventType) -> None:
        """Handle sensor state changes."""
        if (new_state := event.data.get("new_state")) is not None:
            self._update_state(new_state)

    def _update_state(self, state: State) -> None:
        source_value = (
            state.attributes.get(self._source_attribute)
            if self._source_attribute
            else state.state
            if state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)
            else None
        )

        _LOGGER.debug(
            "CalibrationSensor(%s) received update: %s", self.name, source_value
        )

        if not self._source_attribute:
            if self._attr_native_unit_of_measurement is None:
                self._attr_native_unit_of_measurement = state.attributes.get(
                    ATTR_UNIT_OF_MEASUREMENT
                )
            if self._attr_device_class is None:
                self._attr_device_class = state.attributes.get(ATTR_DEVICE_CLASS)
            if self._attr_icon is None:
                self._attr_icon = state.attributes.get(ATTR_ICON)

        try:
            source_value = float(source_value)
            native_value = round(self._poly(source_value), self._precision)
        except (ValueError, TypeError):
            source_value = native_value = None
            if self._source_attribute:
                _LOGGER.warning(
                    "%s attribute %s is not numerical",
                    self._source_entity_id,
                    self._source_attribute,
                )
            else:
                _LOGGER.warning("%s state is not numerical", self._source_entity_id)

        self._attr_extra_state_attributes[ATTR_SOURCE_VALUE] = source_value
        self._attr_native_value = native_value

        self.async_write_ha_state()
