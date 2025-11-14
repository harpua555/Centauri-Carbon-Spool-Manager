# Elegoo Filament Spool Manager

This package provides comprehensive filament tracking for your Elegoo 3D printer.

## Features

- **4 Configurable Spools**: Each spool can be named and tracked independently
- **Automatic Usage Tracking**: Automatically tracks filament usage based on printer extrusion
- **Remaining Filament Calculation**: Real-time calculation of remaining filament
- **Easy Spool Switching**: Quick selection of active spool
- **Dashboard Cards**: Pre-built dashboard cards for easy visualization

## Setup Instructions

### 1. Initial Configuration

After starting Home Assistant, the spool manager will be automatically loaded. You need to configure one setting:

1. Open `config/packages/elegoo_spool_manager.yaml`
2. Find line 248 (the automation trigger)
3. Replace `sensor.elegoo_printer_total_extrusion` with your actual printer's total extrusion sensor entity ID

   **How to find your sensor entity ID:**
   - Go to Developer Tools → States in Home Assistant
   - Search for "total_extrusion"
   - Copy the full entity ID (e.g., `sensor.my_printer_total_extrusion`)

### 2. Configure Your Spools

1. Go to **Settings → Devices & Services → Helpers**
2. You'll see all the spool configuration helpers:
   - **Spool Names**: Rename each spool (e.g., "Black PLA", "White PETG")
   - **Initial Lengths**: Set the starting length of each spool in millimeters
   - **Used Lengths**: These are automatically updated by the system

### 3. Add the Dashboard Card

1. Go to your Home Assistant dashboard
2. Click **Edit Dashboard** (three dots → Edit Dashboard)
3. Click **Add Card** (bottom right)
4. Choose **Manual** card
5. Copy and paste the contents from one of these files:
   - `config/dashboards/elegoo_spool_manager_simple.yaml` (recommended - no custom cards needed)
   - `config/dashboards/elegoo_spool_manager_card.yaml` (requires custom:bar-card)

## Usage

### Starting a New Print

1. **Select Active Spool**: Use the "Active Filament Spool" dropdown to select which spool you're using
2. **Enable Tracking**: Make sure "Enable Spool Tracking" is turned on
3. **Start Printing**: The system will automatically track usage

### Adding a New Spool

1. Select the spool number (1-4) you want to configure
2. **Set Name**: Give it a descriptive name (e.g., "Red PLA - Hatchbox")
3. **Set Initial Length**: Enter the starting amount of filament in millimeters

   **Common conversions:**
   - 1kg PLA spool (1.75mm) ≈ 330,000 mm
   - 1kg PETG spool (1.75mm) ≈ 320,000 mm
   - 1kg ABS spool (1.75mm) ≈ 380,000 mm

4. **Reset Used Length**: Set "Used Length" to 0

### Switching Spools Mid-Print

The system tracks usage per spool, so you can switch between spools at any time:

1. Pause your print (if needed)
2. Change the "Active Filament Spool" selection
3. Resume printing - usage will be tracked to the new spool

### Resetting a Spool

When you install a new spool:

1. Set the "Initial Length" to the new spool's length
2. Set the "Used Length" to 0
3. The "Remaining" will automatically update

## Sensors Created

The package creates the following sensors:

### Control Entities
- `input_select.active_spool` - Select which spool is currently active
- `input_boolean.spool_tracking_enabled` - Enable/disable automatic tracking

### Spool Configuration (per spool)
- `input_text.spool_X_name` - Custom name for the spool
- `input_number.spool_X_initial_length` - Starting length in mm
- `input_number.spool_X_used_length` - Currently used length in mm (auto-updated)

### Calculated Sensors
- `sensor.remaining_filament` - Remaining filament on the active spool
- `sensor.active_spool_name` - Name of the currently active spool
- `sensor.spool_X_remaining` - Remaining filament for each spool (1-4)

Each spool remaining sensor includes attributes:
- `name` - Spool name
- `initial_length` - Starting length
- `used_length` - Used length
- `percent_remaining` - Percentage of filament remaining

## Troubleshooting

### Usage Not Tracking

1. **Check the sensor entity ID**: Make sure line 248 in `elegoo_spool_manager.yaml` has the correct sensor ID
2. **Verify tracking is enabled**: Check that `input_boolean.spool_tracking_enabled` is ON
3. **Confirm active spool**: Make sure an active spool is selected (not "None")
4. **Check automation**: Go to Settings → Automations → Find "Elegoo: Track Filament Usage" and verify it's enabled

### Incorrect Usage Readings

The system tracks cumulative extrusion from the printer. If you:
- Restart Home Assistant: Usage tracking continues normally
- Power cycle the printer: The `total_extrusion` sensor resets, so you should manually note the usage
- Start a new print: Usage continues to accumulate (this is expected behavior)

### Resetting After Printer Restart

If your printer's `total_extrusion` sensor resets to 0 when the printer restarts, you may need to manually update the "Used Length" before starting a new print.

## Advanced Customization

### Adding More Spools

To add more than 4 spools, duplicate the configuration blocks in `elegoo_spool_manager.yaml` and increment the numbers.

### Changing Units

The default unit is millimeters (mm). To use meters:
1. Change all `unit_of_measurement` values from `"mm"` to `"m"`
2. Adjust the `max` values in `input_number` entities accordingly

### Adding Notifications

You can create automations to notify you when a spool is running low:

```yaml
automation:
  - alias: "Low Filament Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.remaining_filament
        below: 50000  # 50 meters
    action:
      - service: notify.notify
        data:
          message: "Warning: Active spool has less than 50m remaining!"
```

## Support

For issues or questions about this spool manager, please open an issue on the repository.
