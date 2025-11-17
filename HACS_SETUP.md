# HACS Setup Instructions

This repository is now configured for HACS (Home Assistant Community Store) integration!

## For Users: Installing via HACS

### Step 1: Add Custom Repository

1. Open **HACS** in your Home Assistant instance
2. Click the **three dots menu (⋮)** in the top right
3. Select **Custom repositories**
4. Enter the following details:
   - **Repository:** `https://github.com/harpua555/Centauri-Carbon-Spool-Manager`
   - **Category:** `Template`
5. Click **ADD**

### Step 2: Download the Integration

1. In HACS, search for "**Centauri Carbon Spool Manager**"
2. Click on the repository
3. Click **Download**
4. Wait for the download to complete

### Step 3: Install Files

After downloading via HACS, you still need to manually copy files to the correct locations:

```bash
# Copy package files (required)
cp config/packages/elegoo_spool_manager.yaml /config/packages/
cp config/packages/elegoo_spool_history.yaml /config/packages/

# Copy dashboard (choose one or more)
cp config/lovelace-spool-manager.yaml /config/
# OR for simple card:
cp config/dashboards/elegoo_spool_manager_simple.yaml /config/dashboards/
```

### Step 4: Configure Home Assistant

1. Add to your `configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

2. Restart Home Assistant

3. Follow the [README.md](README.md) for entity configuration

## For Maintainers: Repository Configuration

### Files for HACS

This repository includes the following HACS-specific files:

- **`hacs.json`** - HACS configuration file
  - Specifies name, compatibility, and structure
  - Located in repository root

- **`info.md`** - HACS display information
  - Shown in HACS UI when viewing the repository
  - Contains quick overview and installation steps

### HACS Configuration

The `hacs.json` file contains:

```json
{
  "name": "Centauri Carbon Spool Manager",
  "content_in_root": false,
  "render_readme": true,
  "homeassistant": "2024.1.0"
}
```

**Field Explanations:**
- `name`: Display name in HACS
- `content_in_root`: Files are in subdirectories (not root)
- `render_readme`: Show README in HACS UI
- `homeassistant`: Minimum Home Assistant version required

### Repository Type

This is a **Template** repository type in HACS because it provides:
- YAML configuration files (not Python code)
- Home Assistant packages
- Lovelace dashboard configurations

### Validation

To validate the HACS configuration:

1. **Via GitHub Actions:**
   - Use the official HACS action in `.github/workflows/`
   - Validates on every push

2. **Manually:**
   - Add as custom repository in HACS
   - Check for any validation errors
   - Ensure all files download correctly

### Releases

HACS uses GitHub releases for versioning:

1. Create releases following semantic versioning (v1.0.0, v1.1.0, etc.)
2. HACS will show the latest release version
3. Users can update through HACS when new releases are published

### Adding to HACS Default Repositories (Optional)

To submit this to the official HACS default repository list:

1. Ensure all requirements are met
2. Submit a PR to: https://github.com/hacs/default
3. Add repository to `template.json`
4. Wait for review and approval

Once approved, users won't need to add as a custom repository.

## Repository Topics

For better discoverability, add these GitHub topics to the repository:

- `home-assistant`
- `hacs`
- `3d-printer`
- `filament-tracking`
- `elegoo`
- `centauri-carbon`
- `automation`
- `homeassistant-configuration`

## Support

For issues related to:
- **HACS installation:** Check [HACS documentation](https://hacs.xyz/)
- **Spool manager setup:** See [README.md](README.md) and [SPOOL_MANAGER.md](SPOOL_MANAGER.md)
- **Bugs or features:** Open an [issue](https://github.com/harpua555/Centauri-Carbon-Spool-Manager/issues)
