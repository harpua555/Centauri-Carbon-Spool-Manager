"""Constants for the Centauri Carbon Spool Manager integration."""

DOMAIN = "centauri_spool_manager"

# Config flow
CONF_PRINTER_DEVICE = "printer_device"
CONF_NUM_SPOOLS = "num_spools"

# Material types
MATERIAL_TYPES = ["Custom", "PLA", "PETG", "ABS", "TPU", "Nylon", "ASA"]

# Material densities (g/cm³)
MATERIAL_DENSITIES = {
    "Custom": 1.24,
    "PLA": 1.24,
    "PETG": 1.27,
    "ABS": 1.04,
    "TPU": 1.21,
    "Nylon": 1.14,
    "ASA": 1.05,
}

# Default filament diameter (mm)
DEFAULT_FILAMENT_DIAMETER = 1.75

# Entity platforms
PLATFORMS = ["sensor", "number", "select", "text", "switch"]
