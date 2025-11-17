# Centauri Carbon Spool Manager - Custom Integration

This directory contains the Home Assistant custom integration for the Centauri Carbon Spool Manager.

## What Gets Installed

When you install this integration via HACS, the following files are automatically copied to your Home Assistant:

### Package Files
Located in `custom_components/centauri_spool_manager/packages/`:
- `elegoo_spool_manager.yaml` - Core spool tracking with material/density support
- `elegoo_spool_history.yaml` - Print history logging and undo functionality

### Dashboard Files
Located in `custom_components/centauri_spool_manager/dashboards/`:
- `lovelace-spool-manager.yaml` - Full dashboard with all features
- `elegoo_spool_manager_simple.yaml` - Minimal card
- `elegoo_spool_manager_with_history.yaml` - Card with history
- `elegoo_spool_manager_card.yaml` - Standalone card
- `spool_1_history.yaml` - History page template

## Post-Installation Steps

After HACS installs this integration, you need to:

### 1. Enable Packages

Add to your `configuration.yaml`:
```yaml
homeassistant:
  packages: !include_dir_merge_named custom_components/centauri_spool_manager/packages
```

### 2. Configure Printer Entity Names

Edit the package files to match your printer:
- `/config/custom_components/centauri_spool_manager/packages/elegoo_spool_manager.yaml`
- `/config/custom_components/centauri_spool_manager/packages/elegoo_spool_history.yaml`

Replace `centauri_carbon` with your printer name in all sensor references.

### 3. Add Dashboard

Copy the dashboard file you want to use from:
`/config/custom_components/centauri_spool_manager/dashboards/`

to your `/config/` directory or add the YAML manually to your existing dashboard.

### 4. Restart Home Assistant

Settings → System → Restart

## Documentation

For complete setup and usage instructions, see the main [README](https://github.com/harpua555/Centauri-Carbon-Spool-Manager/blob/main/README.md).
