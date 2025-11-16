# Centauri Carbon Spool Manager

**Automatic filament tracking for your Elegoo Centauri Carbon (and other FDM printers)**

Track and manage your 3D printer filament spools with automatic usage tracking based on real-time extrusion data from your printer. Works with any Elegoo FDM printer that provides extrusion sensors through the [Elegoo Printer Integration](https://github.com/danielcherubini/elegoo-homeassistant).

## Prerequisites

- Home Assistant instance
- [Elegoo Printer Integration](https://github.com/danielcherubini/elegoo-homeassistant) already installed and configured
- Elegoo FDM printer with extrusion sensor (Centauri Carbon, Neptune 4, OrangeStorm Giga, etc.)

## Features

- **4 Spool Tracking** - Manage up to 4 different filament spools simultaneously
- **Material & Density Profiles** - Built-in profiles for PLA, PETG, ABS, TPU, Nylon, and PC
- **Automatic Usage Tracking** - Real-time tracking using extrusion data from your printer
- **Dual Unit Display** - View remaining filament in both length (mm) and weight (grams)
- **Print History** - Complete log of every print with detailed filament usage
- **Undo Last Print** - Accidentally logged a failed print? Restore filament with one click
- **Multiple Dashboard Options** - Choose from simple, detailed, or history-focused views
- **Persistent Storage** - All data survives Home Assistant restarts
- **Weight-Based Setup** - Enter spool weight, length is calculated automatically

## Installation

### Method 1: Download ZIP (Recommended)

1. **Download** the latest release:
   - Go to [Releases](https://github.com/harpua555/Centauri-Carbon-Spool-Manager/releases)
   - Download `Centauri-Carbon-Spool-Manager.zip`

2. **Extract** the ZIP file

3. **Copy files** to Home Assistant:
   ```bash
   # Copy both package files
   cp config/packages/elegoo_spool_manager.yaml /config/packages/
   cp config/packages/elegoo_spool_history.yaml /config/packages/

   # Copy your preferred dashboard
   cp config/lovelace-spool-manager.yaml /config/
   ```

### Method 2: Git Clone

```bash
git clone https://github.com/harpua555/Centauri-Carbon-Spool-Manager.git

# Copy files to Home Assistant
cp Centauri-Carbon-Spool-Manager/config/packages/*.yaml /config/packages/
cp Centauri-Carbon-Spool-Manager/config/lovelace-spool-manager.yaml /config/
```

### Method 3: Direct File Download

1. Browse to [this repository](https://github.com/harpua555/Centauri-Carbon-Spool-Manager)
2. Navigate to each file under `config/packages/` and `config/`
3. Click "Raw" and save to your Home Assistant config directory

## Setup

### 1. Enable Packages

Add this to your `configuration.yaml` if not already present:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

### 2. Install Dashboard

Choose one of these options:

#### Option A: Full Dashboard (Recommended)

Copy the complete dashboard:
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

For existing dashboards:
```bash
cp config/dashboards/elegoo_spool_manager_simple.yaml /config/dashboards/
```
Then add manually via UI: Settings → Dashboards → Edit → Add Card → Manual YAML

#### Option C: Card with History

Collapsible card with history navigation:
```bash
cp config/dashboards/elegoo_spool_manager_with_history.yaml /config/dashboards/
```

### 3. Restart Home Assistant

## Configuration

### Initial Setup

1. **Navigate** to the Spool Manager dashboard
2. **For each spool:**
   - Set name (e.g., "Red PLA", "Black PETG")
   - Select material type (PLA, PETG, ABS, etc.)
   - Density auto-populates based on material
   - Enter initial weight in grams (e.g., 1000 for 1kg spool)
   - Length calculates automatically

3. **Set filament diameter** (usually 1.75mm)
4. **Select active spool** from dropdown
5. **Enable tracking**

### Entity Name Customization

**Default configuration** assumes entities like:
- `sensor.centauri_carbon_current_status`
- `sensor.centauri_carbon_total_extrusion`
- `sensor.centauri_carbon_file_name`

**If your printer has a different name**, update references in both package files:

```yaml
# Find and replace in:
# - config/packages/elegoo_spool_manager.yaml
# - config/packages/elegoo_spool_history.yaml

# Replace:
sensor.centauri_carbon_current_status
sensor.centauri_carbon_total_extrusion
sensor.centauri_carbon_file_name

# With your printer name:
sensor.YOUR_PRINTER_NAME_current_status
sensor.YOUR_PRINTER_NAME_total_extrusion
sensor.YOUR_PRINTER_NAME_file_name
```

## Usage

### During Printing

1. Select active spool before starting print
2. System automatically:
   - Captures starting state when printing begins
   - Tracks extrusion every 60 seconds during print
   - Logs final usage when print completes/stops
   - Updates spool's used length

### After Printing

- View remaining filament (length & weight)
- Check last print's usage
- Navigate to history for detailed logs
- Undo last print if needed

### Managing Spools

**When spool is empty:**
1. Click "Mark as Empty"
2. Click "Reset Spool (New Spool)"
3. Update name/material if needed
4. Enter new spool weight

## What's Included

### Package Files
- `elegoo_spool_manager.yaml` - Core spool tracking with material/density support
- `elegoo_spool_history.yaml` - Print history logging and undo functionality

### Dashboards
- `lovelace-spool-manager.yaml` - Full dashboard with all features and history views
- `elegoo_spool_manager_simple.yaml` - Minimal card for existing dashboards
- `elegoo_spool_manager_card.yaml` - Standalone card version
- `elegoo_spool_manager_with_history.yaml` - Collapsible card with history links
- `spool_1_history.yaml` - Detailed history page template

### Documentation
- `SPOOL_MANAGER.md` - Complete setup and configuration guide
- `SPOOL_HISTORY_GUIDE.md` - Print history and tracking details
- `RELEASE.md` - Guide for maintainers creating releases

## Material Densities

Included material profiles:
- **PLA:** 1.24 g/cm³
- **PETG:** 1.27 g/cm³
- **ABS:** 1.04 g/cm³
- **TPU:** 1.21 g/cm³
- **Nylon:** 1.14 g/cm³
- **PC (Polycarbonate):** 1.20 g/cm³

Custom/specialty filaments can have density manually adjusted.

## Troubleshooting

### Print history not showing
1. Verify automations are enabled (Settings → Automations & Scenes)
2. Check printer entity names match package configuration
3. Use Developer Tools → States to verify entity values during print
4. Review Home Assistant logs for errors

### Usage not updating
1. Confirm "Enable Tracking" is on
2. Verify active spool is selected
3. Check `sensor.YOUR_PRINTER_NAME_total_extrusion` exists and updates
4. Ensure extrusion sensor reports in millimeters

### Wrong weight calculations
1. Verify material density is correct
2. Check filament diameter (1.75mm vs 2.85mm)
3. Confirm initial weight in grams (not kilograms)

## Support & Contributing

- **Issues:** [GitHub Issues](https://github.com/harpua555/Centauri-Carbon-Spool-Manager/issues)
- **Discussions:** [GitHub Discussions](https://github.com/harpua555/Centauri-Carbon-Spool-Manager/discussions)
- **Pull Requests:** Contributions welcome!

## Related Projects

- [Elegoo Printer Integration](https://github.com/danielcherubini/elegoo-homeassistant) - Required integration for Elegoo printers
- [Home Assistant](https://www.home-assistant.io/) - Open source home automation platform

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Created for the Elegoo Centauri Carbon and compatible FDM printers. Works with any printer providing extrusion data through the Elegoo Printer Integration.
