# Centauri Carbon Spool Manager

**Automatic filament tracking for your Elegoo Centauri Carbon (and other FDM printers)**

Track and manage your 3D printer filament spools with automatic usage tracking based on real-time extrusion data from your printer.

## Features

- **4 Spool Tracking** - Manage up to 4 different filament spools simultaneously
- **Material & Density Profiles** - Built-in profiles for PLA, PETG, ABS, TPU, Nylon, and ASA
- **Automatic Usage Tracking** - Real-time tracking using extrusion data from your printer
- **Dual Unit Display** - View remaining filament in both length (mm) and weight (grams)
- **Print History** - Complete log of every print with detailed filament usage
- **Undo Last Print** - Accidentally logged a failed print? Restore filament with one click
- **Multiple Dashboard Options** - Choose from simple, detailed, or history-focused views
- **Persistent Storage** - All data survives Home Assistant restarts
- **Weight-Based Setup** - Enter spool weight, length is calculated automatically

## Requirements

- Home Assistant 2024.1.0 or later
- [Elegoo Printer Integration](https://github.com/danielcherubini/elegoo-homeassistant) already installed and configured
- Elegoo FDM printer with extrusion sensor (Centauri Carbon, Neptune 4, etc.)

## Installation via HACS (One-Click!)

1. Open HACS in Home Assistant
2. Click **Integrations**
3. Click the three dots menu (⋮) → **Custom repositories**
4. Add repository URL: `https://github.com/harpua555/Centauri-Carbon-Spool-Manager`
5. Select category: **Integration**
6. Click **ADD**
7. Search for "Centauri Carbon Spool Manager" and click **Download**
8. Restart Home Assistant
9. Add to your `configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_merge_named custom_components/centauri_spool_manager/packages
   ```
10. Configure printer entity names and add dashboard

See the full [README](https://github.com/harpua555/Centauri-Carbon-Spool-Manager/blob/main/README.md) for complete setup instructions.

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

## Quick Start

1. Enable packages in `configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

2. Copy package files to `/config/packages/`

3. Update printer entity names in the package files to match your printer

4. Restart Home Assistant

5. Add dashboard cards from the included options

For complete setup instructions, see [SPOOL_MANAGER.md](https://github.com/harpua555/Centauri-Carbon-Spool-Manager/blob/main/SPOOL_MANAGER.md)
