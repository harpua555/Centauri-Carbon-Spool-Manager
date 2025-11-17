# Centauri Carbon Spool Manager - Python Branch

This is a pure Python custom integration - no configuration.yaml editing required. All entities are created automatically when you add the integration.

## Quick Start

### Installation

**Option A: HACS (Recommended)**

1. **HACS** → **Integrations** → **⋮** → **Custom repositories**
2. Add repository: `https://github.com/harpua555/Centauri-Carbon-Spool-Manager`
3. Category: **Integration**
4. Click **Download** and **Restart** Home Assistant

**Option B: Manual Installation**

1. Download or clone this repository
2. Copy the `custom_components/centauri_spool_manager` folder to your Home Assistant
3. Place it in `/config/custom_components/centauri_spool_manager`
4. **Restart** Home Assistant

**Either way, then:**

1. **Settings** → **Devices & Services** → **Add Integration**
2. Search "**Centauri Carbon Spool Manager**"
3. Select your printer from the dropdown
4. Choose number of spools (2-4)
5. Done!

### First Use

1. **Set up a spool:**
   - Give it a name (use the text entity)
   - Choose material type (PLA, PETG, etc.) - density auto-updates
   - **Set initial weight** using the "Set Weight" number entity (in grams)
     - This automatically calculates the filament length

2. **Select active spool** and **enable tracking**

3. **Start printing!** Usage is tracked automatically.

### Using the UI

All controls are available directly in the Home Assistant UI:

**Setting up a new spool:**
- Navigate to the integration's entities
- Change "Spool X Set Weight" to your filament weight in grams
- Set the name and material type
- That's it! Length is calculated automatically

**Managing spools:**
- **Reset Spool** button - Prepare for a new filament roll
- **Mark Empty** button - Mark spool as used up
- **Undo Last Print** button - Restore filament if wrong spool selected

**Quick Dashboard:**
- Copy the YAML from `custom_components/centauri_spool_manager/lovelace/dashboard.yaml`
- Paste into a new dashboard card
- Shows all spools with controls and status

## What You Get

**For each spool, you'll see:**
- Name, material type, and density settings
- Remaining filament (length & weight)
- Percentage remaining
- Last print usage

**Controls available:**
- **Set Weight** number entity - Set weight in grams, length calculated automatically
- **Reset Spool** button - Prepare for new filament roll
- **Undo Last Print** button - Restore if wrong spool selected
- **Mark Empty** button - Mark spool as used up

**Services (for automation):**
- `centauri_spool_manager.set_spool_weight`
- `centauri_spool_manager.reset_spool`
- `centauri_spool_manager.undo_last_print`
- `centauri_spool_manager.mark_spool_empty`

## Example: Setting Up Your First Spool

**Using the UI (Recommended):**

1. Go to **Settings → Devices & Services → Centauri Carbon Spool Manager**
2. Find "Spool 1 Set Weight" and change it to 1000 (grams)
3. Set "Spool 1 Name" to "Red PLA"
4. Set "Spool 1 Material" to "PLA"
5. Set "Active Spool" to "Spool 1"
6. Turn on "Enable Spool Tracking"

**Using Services (for automation):**

```yaml
# 1. Set the weight (calculates length automatically)
service: centauri_spool_manager.set_spool_weight
data:
  spool_number: 1
  weight_grams: 1000

# 2. Name it
service: text.set_value
data:
  entity_id: text.centauri_spool_manager_spool_1_name
  value: "Red PLA"

# 3. Select material type
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

**Full Dashboard:**

Copy the complete dashboard YAML from:
`custom_components/centauri_spool_manager/lovelace/dashboard.yaml`

This includes all spools with full controls and status information.

**Simple Single Spool Card:**

```yaml
type: entities
title: Spool 1
entities:
  - entity: text.centauri_spool_manager_spool_1_name
  - entity: select.centauri_spool_manager_spool_1_material
  - entity: number.centauri_spool_manager_spool_1_set_weight
    name: Set Weight
  - type: divider
  - entity: sensor.centauri_spool_manager_spool_1_remaining_weight
    name: Remaining
  - entity: sensor.centauri_spool_manager_spool_1_percentage_remaining
    name: "%"
  - type: divider
  - type: button
    name: Reset Spool
    tap_action:
      action: call-service
      service: button.press
      target:
        entity_id: button.centauri_spool_manager_spool_1_reset
  - type: button
    name: Mark Empty
    tap_action:
      action: call-service
      service: button.press
      target:
        entity_id: button.centauri_spool_manager_spool_1_mark_empty
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
