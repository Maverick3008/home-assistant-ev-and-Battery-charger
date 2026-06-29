"""Constants for the EV and Battery Charger integration."""

DOMAIN = "ev_and_battery_charger"

CONF_NAME = "name"
CONF_SOC_SENSOR = "soc_sensor"
CONF_TARGET_SOC_ENTITY = "target_soc_entity"
CONF_TARGET_TIME = "target_time"
CONF_BATTERY_SIZE_KWH = "battery_size_kwh"
CONF_CHARGE_POWER_KW = "charge_power_kw"
CONF_EFFICIENCY = "efficiency"
CONF_BUFFER_MINUTES = "buffer_minutes"

DEFAULT_NAME = "EV and Battery Charger"
DEFAULT_BATTERY_SIZE_KWH = 19.7
DEFAULT_CHARGE_POWER_KW = 10.5
DEFAULT_EFFICIENCY = 0.93
DEFAULT_BUFFER_MINUTES = 30
DEFAULT_TARGET_TIME = "06:00:00"

INVALID_STATES = {"unknown", "unavailable", "none", "None", ""}
