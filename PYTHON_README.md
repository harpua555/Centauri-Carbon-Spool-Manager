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
5. Done! (Check the logs for dashboard setup instructions)

### Dashboard Setup

After installing the integration, add the dashboard:

1. Go to **Settings** → **Dashboards** → **Add Dashboard**
2. Name it "Spool Manager"
3. Click the **⋮** menu → **Edit Dashboard** → **Raw configuration editor**
4. Copy the YAML from `custom_components/centauri_spool_manager/lovelace/dashboard.yaml`
5. Paste it in and save

### First Use

**Spools start locked by default** to prevent accidental changes.

**Option A: Using the Setup Service (Recommended)**

Use the `setup_spool` service to configure everything at once:

```yaml
service: centauri_spool_manager.setup_spool
data:
  spool_number: 1
  name: "Red PLA"
  material: "PLA"
  weight_grams: 1000
  auto_lock: true  # Optional, defaults to true
```

This automatically unlocks, configures, and locks the spool.

**Option B: Manual Configuration**

1. Click "Reset Spool" button to unlock
2. Configure name, material, and weight
3. Click the lock toggle to lock it again

**Then:**
1. Go to Overview tab
2. Select active spool
3. Enable tracking
4. Start printing!

The dashboard includes:
- **Overview tab** - All spools at a glance with gauge indicators
- **Individual spool tabs** - Full configuration and statistics for each spool
- **Color-coded gauges** - Green (>50%), Yellow (20-50%), Red (<20%)
- **Lock switches** - Prevent accidental modifications during printing
- **Quick actions** - Reset, Mark Empty (Quick Reload), Undo Last Print

### Using the UI

All controls are available directly in the Home Assistant UI:

**Setting up a new spool:**
- Navigate to the integration's entities
- Change "Spool X Set Weight" to your filament weight in grams
- Set the name and material type
- That's it! Length is calculated automatically

**Managing spools:**
- **Lock/Unlock** - Protect configuration during printing
- **Reset Spool** button - Clear spool for new filament (auto-unlocks first)
- **Mark Empty (Quick Reload)** button - Mark as empty and reset with same initial weight
- **Undo Last Print** button - Restore filament if wrong spool selected

**Dashboard:**
- Ready-to-use YAML provided in `lovelace/dashboard.yaml`
- Shows overview of all spools with gauges
- Individual tabs for detailed spool configuration
- See "Dashboard Setup" section above for installation

## What You Get

**For each spool, you'll see:**
- Name, material type, and density settings
- **Spool state** - ready, configured, active, or empty
- Remaining filament (length & weight)
- Percentage remaining with color-coded gauge
- Last print usage for undo functionality

**Controls available:**
- **Lock Switch** - Prevent accidental changes during printing
- **Set Weight** number entity - Set weight in grams, length calculated automatically
- **Reset Spool** button - Prepare for new filament roll (auto-unlocks)
- **Mark Empty (Quick Reload)** button - Reset with same initial conditions
- **Undo Last Print** button - Restore filament if wrong spool selected

**Services (for automation):**
- `centauri_spool_manager.set_spool_weight`
- `centauri_spool_manager.reset_spool`
- `centauri_spool_manager.undo_last_print`
- `centauri_spool_manager.mark_spool_empty`

## Example: Setting Up Your First Spool

**Using the Dashboard (Recommended):**

1. Open the **Spool Manager** dashboard from the sidebar
2. Click on the **Spool 1** tab
3. Configure the spool:
   - Set name to "Red PLA"
   - Select material "PLA"
   - Set initial weight to 1000 grams
   - **Turn on Lock** to protect configuration
4. Go to **Overview** tab
5. Set "Active Spool" to "Spool 1"
6. Turn on "Enable Spool Tracking"
7. Start printing!

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

## Features Deep Dive

### Lock Protection

The lock switch prevents accidental modifications while printing:
- When **locked**, you cannot change: name, material, weight, or density
- Reset and Mark Empty buttons automatically unlock the spool first
- Recommended workflow: Configure → Lock → Print → Empty → Unlock → Reconfigure

### Quick Reload

The "Mark Empty" button now implements Quick Reload:
1. Stores current spool configuration (name, material, weight)
2. Marks the spool as empty
3. Unlocks the spool
4. Resets all usage counters
5. **Restores the initial weight** automatically

This allows you to quickly reload the same filament type without reconfiguring.

### Spool States

Each spool tracks its lifecycle state:
- **ready** - No configuration yet
- **configured** - Has weight/material set but not active
- **active** - Currently selected for printing
- **empty** - Marked as used up (used ≥ initial length)

## Manual Dashboard Setup

If you need to manually recreate the dashboard:

**Full Dashboard:**

Copy the complete dashboard YAML from:
`custom_components/centauri_spool_manager/lovelace/dashboard.yaml`

Then add it as a new dashboard in Home Assistant.

**Simple Single Spool Card (for custom dashboards):**

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
