# Spool History & Undo Feature Guide

Your spool manager now includes print history tracking with undo functionality!

## ✨ What's New

### Features Added

1. **📜 Print History Tracking**
   - Automatically logs when prints complete
   - Tracks length and weight used per print
   - Stores history in Home Assistant's logbook

2. **🔄 Undo Last Print**
   - One-click restore of filament from last print
   - Useful when wrong spool was selected
   - Confirmation dialog prevents accidents

3. **📊 Detailed History Pages**
   - Dedicated page for each spool
   - View usage graphs over time
   - See complete print history

4. **📈 Statistics**
   - Last print length and weight
   - Usage trends
   - Remaining filament visualization

## 🚀 Setup Instructions

### Step 1: Restart Home Assistant

The new history package will be automatically loaded:
```bash
make start
```

### Step 2: Configure Print Status Sensor

Edit `config/packages/elegoo_spool_history.yaml` and update line 58 and 85:

```yaml
# Change this:
entity_id: sensor.elegoo_printer_print_status

# To your actual print status sensor, for example:
entity_id: sensor.my_printer_print_status
```

**How to find your sensor:**
1. Go to Developer Tools → States
2. Search for "print_status" or "status"
3. Find the sensor that shows "printing", "complete", etc.
4. Copy the full entity ID

### Step 3: Create History Dashboard Views

You have two options:

#### Option A: Simple (No History Pages)
Use the existing simple dashboard - adds "Undo" buttons inline

#### Option B: Full History (Recommended)
1. Go to Settings → Dashboards
2. Create 4 new views (one per spool):
   - View 1: "Spool 1 History" (path: `/lovelace-spool1`)
   - View 2: "Spool 2 History" (path: `/lovelace-spool2`)
   - View 3: "Spool 3 History" (path: `/lovelace-spool3`)
   - View 4: "Spool 4 History" (path: `/lovelace-spool4`)
3. For each view, paste the content from `config/dashboards/spool_1_history.yaml` (adjust spool number)

## 📱 Using the History Features

### Viewing Last Print

On the main dashboard, each spool shows:
- **Last Print Length**: How much filament was used
- **Last Print Weight**: Weight of filament used
- **Undo Button**: Restore filament

### Undoing a Print

If you selected the wrong spool:

1. Click **"🔄 Undo Last Print"** button
2. Confirm the restoration
3. Filament is immediately restored
4. You'll see a notification confirming the undo

### Viewing Full History

1. Click on a spool's **"📜 View Full History"** button
2. See detailed graphs showing:
   - Remaining filament over time
   - Usage statistics
   - Complete print log
3. Access quick actions like:
   - Reset spool (for new spool)
   - Mark as empty
   - Undo last print

## 🔧 How It Works

### Automatic Tracking

When a print completes:
1. System logs the print to Home Assistant's logbook
2. Saves the "before print" usage amount
3. Calculates used length and weight
4. Updates spool sensors

### Undo Mechanism

When you undo:
1. Restores the "used length" to the pre-print value
2. Remaining length automatically recalculates
3. Weight sensors update based on new length

### History Storage

- **Last print**: Stored in `input_number.spool_X_last_used_length`
- **Full history**: Available in Home Assistant's logbook and history
- **Statistics**: Built from sensor history data

## 📊 Dashboard Options

### Fold Entity Row (Collapsible)

The main dashboard uses `custom:fold-entity-row` for collapsible sections. If you don't have this installed:

**Install from HACS:**
1. HACS → Frontend
2. Search "fold-entity-row"
3. Install and refresh browser

**Or use simple version:**
Use `elegoo_spool_manager_simple.yaml` which doesn't require custom cards.

## 🎯 Example Workflow

### Scenario: Printed with Wrong Spool

1. **During print:**
   - You selected "Spool 1" but loaded "Spool 2"

2. **After print completes:**
   - "Spool 1" shows 1500mm used
   - But you actually used "Spool 2"

3. **To fix:**
   - Go to Spool 1 card
   - Click "🔄 Undo Last Print"
   - Confirm
   - Spool 1 is restored
   - Manually switch to Spool 2
   - Manually add 1500mm to Spool 2's used length

### Scenario: New Spool Installation

1. Navigate to spool's history page
2. Enter new spool details (name, material, weight)
3. Click "Reset Spool (New Spool)"
4. All counters reset to zero
5. Start printing!

## 🛠️ Customization

### Adjust History Retention

By default, History shows 7 days (168 hours). To change:

Edit the dashboard YAML:
```yaml
hours_to_show: 336  # 14 days
```

### Add Print File Names

If you want to track which file was printed, update the automation in `elegoo_spool_history.yaml`:

```yaml
message: >
  Completed print on {{ states('input_text.current_print_spool') }}
  File: {{ states('sensor.YOUR_PRINTER_file_name') }}
  Used: {{ states('sensor.spool_X_last_print_length') }}mm
```

### Custom Notifications

Add notifications when prints complete:

```yaml
action:
  - service: notify.notify
    data:
      title: "Print Complete"
      message: "Used {{ states('sensor.spool_X_last_print_weight') }}g from {{ states('input_text.spool_X_name') }}"
```

## 📈 Statistics & Analytics

The history pages include:

- **7-day graphs**: Visual trends
- **Statistics cards**: Mean, change, min/max
- **Logbook**: Detailed event log
- **Quick stats**: Instant overview

### Example Analytics Questions

The history can answer:
- How much filament did I use this week?
- When did I last print with this spool?
- How long until this spool runs out?
- What's my average usage per day?

## 🚨 Troubleshooting

### Undo Button Doesn't Work

1. Check that print completed (not cancelled)
2. Verify the spool was active during the print
3. Check Home Assistant logs for errors

### History Not Showing

1. Ensure `print_status` sensor is correct
2. Check that automation is enabled
3. Verify logbook integration is working

### Wrong Usage Amount

The system tracks cumulative extrusion. If usage seems off:
1. Check that `total_extrusion` sensor is working
2. Verify the correct sensor is configured
3. Manually adjust the `used_length` if needed

## 📝 Notes

- **Undo only works for last print**: Can't undo multiple prints back
- **History persistence**: Stored in Home Assistant's database
- **Manual adjustments**: You can always manually edit the "Used Length" fields
- **Multiple printers**: Each spool tracks its own history independently

Enjoy your enhanced spool tracking! 🎉
