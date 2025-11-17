# Centauri Carbon Spool Manager

**Automatic filament tracking for your Elegoo Centauri Carbon (and other FDM printers)**

Track and manage your 3D printer filament spools with automatic usage tracking based on real-time extrusion data from your printer. Works with any Elegoo FDM printer that provides extrusion sensors through the [Elegoo Printer Integration](https://github.com/danielcherubini/elegoo-homeassistant).

## Prerequisites

- Home Assistant instance
- [Elegoo Printer Integration](https://github.com/danielcherubini/elegoo-homeassistant) already installed and configured
- Elegoo Centauri Carbon running OpenCentauri patched firmware v 0.x.x or higher (not yet available)

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

### HACS (Recommended - Almost One-Click!)

1. **Open HACS** in Home Assistant
2. Click **Integrations**
3. Click the **three dots menu (⋮)** → **Custom repositories**
4. **Add repository:**
   - URL: `https://github.com/harpua555/Centauri-Carbon-Spool-Manager`
   - Category: **Integration**
5. Click **ADD**
6. Search for "**Centauri Carbon Spool Manager**"
7. Click **Download**
8. **Restart** Home Assistant
9. Go to **Settings** → **Devices & Services**
10. Click **Add Integration** and search for "**Centauri Carbon Spool Manager**"
11. Click to add it
12. Follow the setup wizard

The integration will tell you exactly what to do next in the Home Assistant logs!

## Setup

After installing via HACS, follow these steps to complete the setup:

### 1. Enable Packages

Add this to your `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_merge_named custom_components/centauri_spool_manager/packages
```

**Note:** This loads the package files directly from the integration directory - no manual file copying needed!

### 2. Configure Printer Entity Names

Edit the package files to match your printer name:
- `/config/custom_components/centauri_spool_manager/packages/elegoo_spool_manager.yaml`
- `/config/custom_components/centauri_spool_manager/packages/elegoo_spool_history.yaml`

Replace `centauri_carbon` with your printer name (e.g., `neptune_4`, `my_printer`, etc.)

**Find your printer's entity names:**
1. Go to Developer Tools → States
2. Search for "extrusion" or "print_status"
3. Look for entities like: `sensor.YOUR_PRINTER_total_extrusion`
4. Use that printer name in the package files

### 3. Add Dashboard

**Option A: Full Dashboard (Recommended)**

Add to your `configuration.yaml`:
```yaml
lovelace:
  mode: storage
  dashboards:
    lovelace-spool-manager:
      mode: yaml
      title: Spool Manager
      icon: mdi:printer-3d-nozzle
      show_in_sidebar: true
      filename: custom_components/centauri_spool_manager/dashboards/lovelace-spool-manager.yaml
```

**Option B: Manual Card**

1. Go to your dashboard
2. Edit Dashboard → Add Card → Manual YAML
3. Copy contents from `/config/custom_components/centauri_spool_manager/dashboards/elegoo_spool_manager_simple.yaml`

### 4. Restart Home Assistant

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
