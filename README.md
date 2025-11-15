# Elegoo Printer Filament Spool Manager (Standalone)

**Track and manage your 3D printer filament spools with automatic usage tracking**

This is a standalone filament spool management system for Home Assistant that works with the [Elegoo Printer Integration](https://github.com/danielcherubini/elegoo-homeassistant). It provides automatic filament usage tracking based on extrusion data from your Elegoo FDM printer.

## Prerequisites

- Home Assistant instance
- [Elegoo Printer Integration](https://github.com/danielcherubini/elegoo-homeassistant) already installed and configured
- Elegoo FDM printer (e.g., Neptune 4, OrangeStorm Giga, Centauri Carbon)

## Features

- **4 Spool Tracking** - Track up to 4 different filament spools
- **Material & Density** - Configure material type and density for accurate weight calculations
- **Automatic Usage Tracking** - Automatically tracks filament usage during prints using extrusion data
- **Weight & Length Display** - View remaining filament in both mm and grams
- **Print History** - Log every print with filament usage details
- **Undo Last Print** - Made a mistake? Restore filament from the last print
- **Multiple Dashboards** - Choose from simple, detailed, or history-focused views
- **Persistent Storage** - All data survives Home Assistant restarts

## Installation

### 1. Copy Package Files

Copy the package files to your Home Assistant configuration:

```bash
# Copy both package files to your packages directory
cp config/packages/elegoo_spool_manager.yaml /config/packages/
cp config/packages/elegoo_spool_history.yaml /config/packages/
```

### 2. Enable Packages in Configuration

Add this to your `configuration.yaml` if not already present:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

### 3. Choose and Install Dashboard

Pick one of the dashboard options:

#### Option A: Full Dashboard (Recommended)
Copy the complete dashboard with history views:
```bash
cp config/lovelace-spool-manager.yaml /config/
```

Then add to your `configuration.yaml`:
```yaml
lovelace:
  mode: storage
  dashboards:
    lovelace-spool-manager:
      mode: yaml
      title: Spool Manager
      icon: mdi:printer-3d-nozzle
      show_in_sidebar: true
      filename: lovelace-spool-manager.yaml
```

#### Option B: Simple Card
Copy just the simple card to add to an existing dashboard:
```bash
cp config/dashboards/elegoo_spool_manager_simple.yaml /config/dashboards/
```

Then add the card manually to your dashboard via the UI.

#### Option C: Card with History Links
For a collapsible card with history buttons:
```bash
cp config/dashboards/elegoo_spool_manager_with_history.yaml /config/dashboards/
```

### 4. Restart Home Assistant

Restart Home Assistant to load the new configuration.

## Configuration

### Initial Setup

1. Navigate to the Spool Manager dashboard
2. For each spool you want to track:
   - Set the spool name (e.g., "Red PLA", "Black PETG")
   - Select the material type (PLA, PETG, ABS, TPU, etc.)
   - The density will auto-populate based on material
   - Enter the initial weight in grams (e.g., 1000g for a 1kg spool)
   - The initial length will be automatically calculated

3. Set your filament diameter (usually 1.75mm)
4. Select the active spool from the dropdown
5. Enable tracking

### Entity Name Customization

The automations reference your printer by name. By default, they look for entities like:
- `sensor.centauri_carbon_print_status`
- `sensor.centauri_carbon_total_extrusion`

If your printer has a different name, you'll need to update these references in both package files:

```yaml
# Find and replace in both files:
# sensor.YOUR_PRINTER_NAME_print_status
# sensor.YOUR_PRINTER_NAME_total_extrusion
# sensor.YOUR_PRINTER_NAME_current_status
# sensor.YOUR_PRINTER_NAME_file_name
```

## Usage

### During Printing

1. Select the active spool before starting a print
2. The system will automatically:
   - Capture the starting state when printing begins
   - Track extrusion amount during the print (updated every 60 seconds)
   - Log the final usage when the print completes
   - Update the spool's used length

### After Printing

- View remaining filament in both length (mm) and weight (g)
- Check the last print's filament usage
- Navigate to history view to see all prints for a spool
- Use "Undo Last Print" if you need to restore filament

### Changing Spools

When you finish a spool:
1. Click "Mark as Empty" to set it to fully used
2. Enter a new spool by clicking "Reset Spool (New Spool)"
3. Update the spool name and material if needed
4. Enter the new initial weight

## Files Included

### Core Packages
- `config/packages/elegoo_spool_manager.yaml` - Main spool tracking with weight/density support
- `config/packages/elegoo_spool_history.yaml` - Print history logging and undo functionality

### Dashboards
- `config/lovelace-spool-manager.yaml` - Full dashboard with all features and history views
- `config/dashboards/elegoo_spool_manager_simple.yaml` - Minimal card for existing dashboards
- `config/dashboards/elegoo_spool_manager_card.yaml` - Standalone card version
- `config/dashboards/elegoo_spool_manager_with_history.yaml` - Card with collapsible history
- `config/dashboards/spool_1_history.yaml` - Example detailed history page template

### Documentation
- `SPOOL_MANAGER.md` - Detailed setup and configuration guide
- `SPOOL_HISTORY_GUIDE.md` - Print history and tracking documentation

## Material Densities

The system includes preset densities for common materials:
- PLA: 1.24 g/cm³
- PETG: 1.27 g/cm³
- ABS: 1.04 g/cm³
- TPU: 1.21 g/cm³
- Nylon: 1.14 g/cm³
- PC (Polycarbonate): 1.20 g/cm³

You can manually adjust density for custom or specialty filaments.

## Troubleshooting

### Print history not showing
1. Check that automations are enabled
2. Verify your printer entity names match the automations
3. Check Developer Tools → States to see entity values during a print
4. Review Home Assistant logs for any errors

### Usage not updating
1. Confirm "Enable Tracking" is on
2. Verify the active spool is selected
3. Check that `sensor.YOUR_PRINTER_NAME_total_extrusion` exists and updates
4. Ensure extrusion sensor provides data in millimeters

### Wrong weight calculations
1. Verify the material density is correct
2. Check filament diameter is set correctly (1.75mm or 2.85mm)
3. Ensure initial weight was entered in grams, not kilograms

## Support

For issues, feature requests, or questions about the main integration:
- [GitHub Issues](https://github.com/danielcherubini/elegoo-homeassistant/issues)

For spool manager specific questions:
- Check the detailed guides in `SPOOL_MANAGER.md` and `SPOOL_HISTORY_GUIDE.md`

## License

This project is licensed under the same license as the main Elegoo Printer Integration.

## Credits

Part of the Elegoo Printer Home Assistant Integration project.
