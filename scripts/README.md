# Automation Scripts

This directory contains automation scripts for the demo repository.

## generate_icons.py

Generates demo icons in various sizes for the repository. The script is idempotent - it will produce the same output regardless of how many times it's run.

### Usage

```bash
python scripts/generate_icons.py
```

### Features

- **Idempotent**: Always produces identical results
- **Clean execution**: Removes existing icons before generating new ones
- **Error handling**: Provides clear error messages and proper exit codes
- **Validation**: Verifies all expected icons are generated

### Generated Icons

The script generates PNG icons in the following sizes:
- 16x16 pixels
- 32x32 pixels  
- 64x64 pixels
- 128x128 pixels
- 256x256 pixels

All icons are saved to `assets/icons/` directory.