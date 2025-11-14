# Elegoo Spool Manager Quick Start

The Elegoo Spool Manager is now embedded in this repository and will automatically load when you start Home Assistant.

## What You Get

✅ **4 Renamable Spools** - Each can be customized with a name
✅ **Automatic Usage Tracking** - Tracks filament consumption in real-time
✅ **Active Spool Selection** - Easy dropdown to switch between spools
✅ **Remaining Filament Display** - See how much is left on each spool
✅ **Dashboard Cards** - Pre-built UI cards ready to use

## Quick Setup (3 Steps)

### Step 1: Start Home Assistant

```bash
make start
```

The spool manager is automatically loaded from `config/packages/elegoo_spool_manager.yaml`.

### Step 2: Configure Your Printer Sensor

1. Open `config/packages/elegoo_spool_manager.yaml`
2. Go to line 248
3. Replace `sensor.elegoo_printer_total_extrusion` with your actual sensor entity ID

   **Find your sensor:** Go to Developer Tools → States → search for "total_extrusion"

### Step 3: Add the Dashboard

1. Open your Home Assistant dashboard
2. Click **Edit Dashboard** (three dots menu)
3. Click **Add Card** → **Manual**
4. Copy the contents from: `config/dashboards/elegoo_spool_manager_simple.yaml`
5. Paste and save

## Using the Spool Manager

### Setup a New Spool

1. Go to your spool manager dashboard
2. Enter a name (e.g., "Black PLA")
3. Set initial length in millimeters:
   - **1kg PLA spool (1.75mm)** = 330,000 mm
   - **1kg PETG spool (1.75mm)** = 320,000 mm
   - **1kg ABS spool (1.75mm)** = 380,000 mm
4. Set used length to 0

### Start Tracking

1. Select your active spool from the dropdown
2. Enable "Spool Tracking"
3. Start printing - usage is automatically tracked!

### Switch Spools

Just select a different spool from the "Active Filament Spool" dropdown. Each spool's usage is tracked independently.

## Files Created

```
config/
├── packages/
│   ├── elegoo_spool_manager.yaml  # Main spool manager configuration
│   └── README.md                  # Detailed documentation
├── dashboards/
│   ├── elegoo_spool_manager_simple.yaml  # Simple dashboard (recommended)
│   └── elegoo_spool_manager_card.yaml    # Advanced dashboard
└── configuration.yaml             # Updated to load packages
```

## Features

- **Per-Spool Tracking**: Each spool maintains its own usage counter
- **Real-Time Updates**: Remaining filament updates as you print
- **Percentage Display**: See what % of each spool remains
- **Persistence**: All data survives Home Assistant restarts
- **Multi-Printer Support**: Works with multiple printers (configure separately)

## Troubleshooting

**Not tracking usage?**
- Check that "Enable Spool Tracking" is ON
- Verify an active spool is selected (not "None")
- Confirm the sensor entity ID in line 248 is correct

**Need more details?**
See `config/packages/README.md` for comprehensive documentation.

## Next Steps

After setup, consider:
- Creating low filament alerts (notifications when spool < 50m)
- Adding color/material type fields for each spool
- Integrating with your printer's status display

Enjoy tracking your filament! 🎨
