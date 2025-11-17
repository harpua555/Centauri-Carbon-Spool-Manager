# Centauri Carbon Spool Manager - Python Branch

This is a pure Python custom integration - no configuration.yaml editing required. All entities are created automatically when you add the integration.

## Quick Start

### Installation

1. **HACS** → **Integrations** → **⋮** → **Custom repositories**
2. Add repository: `https://github.com/harpua555/Centauri-Carbon-Spool-Manager`
3. Category: **Integration**
4. **Download** and **Restart** Home Assistant
5. **Settings** → **Devices & Services** → **Add Integration**
6. Search "**Centauri Carbon Spool Manager**"
7. Select your printer from the dropdown
8. Choose number of spools (2-4)
9. Done!

### First Use

1. **Set up a spool:**
   - Give it a name
   - Choose material type (PLA, PETG, etc.)
   - Use service `set_spool_weight` with weight in grams

2. **Select active spool** and **enable tracking**

3. **Start printing!** Usage is tracked automatically.

## What You Get

**For each spool, you'll see:**
- Name, material type, and density settings
- Remaining filament (length & weight)
- Percentage remaining
- Last print usage

**Services available:**
- `set_spool_weight` - Set weight, length calculated automatically
- `reset_spool` - Prepare for new filament roll
- `undo_last_print` - Restore if wrong spool selected
- `mark_spool_empty` - Mark spool as used up

## Example: Setting Up Your First Spool

```yaml
# 1. Set the weight (calculates length automatically)
service: centauri_spool_manager.set_spool_weight
data:
  spool_number: 1
  weight_grams: 1000

# 2. Name it
# Use the UI or:
service: text.set_value
data:
  entity_id: text.centauri_spool_manager_spool_1_name
  value: "Red PLA"

# 3. Select material type
# Use the UI or:
service: select.select_option
data:
  entity_id: select.centauri_spool_manager_spool_1_material
  option: "PLA"

# 4. Make it active
service: select.select_option
data:
  entity_id: select.centauri_spool_manager_active_spool
  option: "Spool 1"

# 5. Enable tracking
service: switch.turn_on
data:
  entity_id: switch.centauri_spool_manager_enable_spool_tracking
```

## Quick Dashboard

Add this to your dashboard for a simple spool card:

```yaml
type: entities
title: Spool 1
entities:
  - entity: text.centauri_spool_manager_spool_1_name
  - entity: select.centauri_spool_manager_spool_1_material
  - entity: sensor.centauri_spool_manager_spool_1_remaining_weight
    name: Remaining
  - entity: sensor.centauri_spool_manager_spool_1_percentage_remaining
    name: "%"
  - type: button
    name: Reset for New Spool
    tap_action:
      action: call-service
      service: centauri_spool_manager.reset_spool
      data:
        spool_number: 1
```

## Troubleshooting

**"No printer found" during setup**
- Install the [Elegoo Printer Integration](https://github.com/danielcherubini/elegoo-homeassistant) first
- Make sure your printer is configured and connected

**Tracking not working**
- Check that tracking switch is ON
- Verify active spool is selected (not "None")
- Ensure printer has `_total_extrusion` and `_current_status` entities

**Wrong weight calculations**
- Verify filament diameter (usually 1.75mm)
- Check material density matches your filament
- Confirm initial weight is in grams, not kilograms

- Issues: [GitHub Issues](https://github.com/harpua555/Centauri-Carbon-Spool-Manager/issues)
- Full docs: See main branch README

## License

MIT License
