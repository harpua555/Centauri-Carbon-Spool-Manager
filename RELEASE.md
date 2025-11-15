# Release Guide

## Creating a New Release

### 1. Ensure all changes are committed

```bash
git status  # Should show clean working tree
```

### 2. Create and push a tag

```bash
# Create a tag (e.g., v1.0.0, v1.1.0, etc.)
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push the tag to GitHub
git push origin v1.0.0
```

### 3. GitHub Actions will automatically:

- Create a ZIP file `centauri-carbon-spool-manager.zip` containing:
  - All package files
  - All dashboard files
  - Documentation
  - Installation script

- Create a GitHub Release with:
  - Release notes
  - Download link
  - Installation instructions

### 4. Release will be available at:

`https://github.com/YOUR_USERNAME/centauri-carbon-spool-manager/releases`

## Tag Naming Convention

Use semantic versioning: `v<MAJOR>.<MINOR>.<PATCH>`

- **MAJOR**: Breaking changes (e.g., v2.0.0)
- **MINOR**: New features, backwards compatible (e.g., v1.1.0)
- **PATCH**: Bug fixes (e.g., v1.0.1)

Examples:
- `v1.0.0` - Initial release
- `v1.0.1` - Bug fix for history logging
- `v1.1.0` - Add new material type (ASA)
- `v2.0.0` - Breaking change to entity names

## Manual Release (Without GitHub Actions)

```bash
# Create release directory
mkdir -p release/config/{packages,dashboards}

# Copy files
cp config/packages/*.yaml release/config/packages/
cp config/dashboards/*.yaml release/config/dashboards/
cp config/lovelace-spool-manager.yaml release/config/
cp README.md SPOOL_MANAGER.md SPOOL_HISTORY_GUIDE.md LICENSE release/

# Create ZIP
cd release && zip -r ../centauri-carbon-spool-manager.zip . && cd ..
```

Then upload to GitHub Releases manually.

## Troubleshooting

### GitHub Actions not triggering

- Verify tag format matches `v*` (e.g., v1.0.0)
- Check that you pushed the tag: `git push origin v1.0.0`
- Look at Actions tab on GitHub for error messages

### Release ZIP missing files

- Check `.github/workflows/release-standalone.yml`
- Verify file paths are correct
- Test locally by running the archive commands

### Users reporting installation issues

1. Test the installation script yourself
2. Update README.md with clearer instructions
3. Check GitHub Issues for common problems
