# MambuPy Utilities

This directory contains utility scripts for common Mambu administration tasks.

## Available Scripts

### update_user_roles.py

Update user roles in Mambu from a CSV file.

**Features:**
- Validates all roles exist before making any changes
- Validates CSV file format
- Skips non-existent users with warnings
- Supports comment lines (starting with `#`)
- Provides dry-run mode for testing
- Detailed logging and processing summary

**Usage:**
```bash
# Basic usage
python update_user_roles.py users_roles.csv

# Dry run (validate without making changes)
python update_user_roles.py users_roles.csv --dry-run

# Custom CSV format
python update_user_roles.py users_roles.csv --username-col 0 --role-col 2

# Tab-separated values
python update_user_roles.py users_roles.tsv --delimiter $'\t'

# Verbose output
python update_user_roles.py users_roles.csv --verbose
```

**CSV Format:**
```csv
username,role
john.doe,Credit Officer
jane.smith,BRANCH_MANAGER_ID
# This is a comment
bob.johnson,Accountant
```

Roles can be specified by **name** OR by **ID**. See `sample_user_roles.csv` for a complete example.

**Arguments:**
- `csv_file`: Path to CSV file containing username and role columns (required)
- `--username-col N`: Zero-indexed column number for usernames (default: 0)
- `--role-col N`: Zero-indexed column number for roles (default: 1)
- `--delimiter CHAR`: CSV delimiter character (default: ",")
- `--dry-run`: Validate data but don't actually update users
- `--verbose`: Enable verbose logging (DEBUG level)

**Validation:**
1. All specified roles must exist in Mambu (checked at startup)
2. CSV file must have valid format with required columns
3. Non-existent users are skipped with warnings (not errors)
4. Empty usernames or roles are skipped

---

### userdeactivate.py

Deactivate multiple users from a CSV list.

**Usage:**
```bash
python userdeactivate.py users_list.csv
```

**CSV Format:**
```csv
username
john.doe
jane.smith
```

The script:
- Verifies users have no active loans with balances
- Unassigns user groups
- Sets user state to INACTIVE

---

## Configuration

All scripts use MambuPy's configuration system. Ensure you have configured your Mambu connection in one of:
- `~/.mambupy.rc`
- `/etc/mambupy.rc`
- Environment variables (`MAMBUPY_APIURL`, `MAMBUPY_APIUSER`, `MAMBUPY_APIPWD`)
- Command-line arguments

Example RC file:
```ini
[API]
apiurl=https://your-domain.mambu.com
apiuser=your_api_user
apipwd=your_api_password
```

## Requirements

These scripts require MambuPy to be installed:
```bash
pip install MambuPy
```

Or for development:
```bash
pip install -e ".[dev]"
```

## Contributing

When adding new utility scripts:
1. Follow the existing code style
2. Add comprehensive documentation
3. Include error handling and validation
4. Provide sample data files
5. Update this README
