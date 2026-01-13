# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MambuPy is a Python library for interacting with Mambu (a cloud lending platform). The library supports two distinct approaches:

1. **REST API Integration** - Primary interface using Mambu's REST API (v1 and v2)
2. **ORM Interface** - Direct database access using SQLAlchemy for DB backups

The project is currently at version 2.1.0 and supports Python 3.7+.

## Architecture

### Dual API Architecture

MambuPy maintains **two separate REST API implementations**:

- **`MambuPy.api.*`** - Modern API v2 implementation (actively developed)
  - Located in `MambuPy/api/`
  - Uses `MambuConnectorREST` for HTTP communication
  - Implements entities as `MambuEntity` subclasses with mixins (Writable, Searchable, Attachable, Commentable, Ownable)
  - Session management via `SessionSingleton` pattern for connection reuse

- **`MambuPy.rest.*`** - Legacy API v1 implementation (deprecated but maintained)
  - Located in `MambuPy/rest/`
  - Older REST implementation using `MambuStruct` base class
  - Kept for backward compatibility

### Core Components

- **`mambuconfig.py`** - Configuration management supporting:
  - RC files (`~/.mambupy.rc`, `/etc/mambupy.rc`)
  - Environment variables (`MAMBUPY_*`)
  - Command-line arguments (`mambupy_*`)

- **`mambugeturl.py`** - URL construction for Mambu REST endpoints

- **`mambuutil.py`** - Utility functions, error classes, and constants

- **`MambuPy/api/connector/`** - REST connector implementations
  - `rest.py` - Main REST connector with retry logic and session management
  - `mambuconnector.py` - Base connector classes (Reader/Writer)

- **`MambuPy/api/entities.py`** - Base entity classes and custom field handling

- **`MambuPy/api/interfaces.py`** - ABC interfaces for entity capabilities

- **`MambuPy/orm/`** - SQLAlchemy schemas for database access (optional, requires `full` dependencies)

### Custom Fields Architecture

Custom fields (`_customFields`) are extracted into separate CF objects during entity instantiation. They're stored in a dedicated structure and must be explicitly updated before write operations (update/create/patch).

### TimeZone Handling

Datetime fields lose timezone info when converted to Python datetimes. TZ information is preserved separately in the `_tzattrs` dictionary, allowing TZ-naive datetime comparisons in user code.

## Development Commands

### Testing

Run all tests:
```bash
make test
```

Run tests without API v2 tests:
```bash
make test APIV2=no
```

Run a single test:
```bash
coverage run --append --rcfile=./.coveragerc tests/unit_mambuconfig.py
```

Run API v2 specific tests:
```bash
coverage run --append --rcfile=./.coveragerc tests/api/unit_mambuloan.py
```

### Linting

Run legacy linter (pylint):
```bash
make lint
```

Run modern linters (ruff, black, isort):
```bash
make lint2
```

Auto-fix linting issues:
```bash
make lint2-fix
```

### Building

Build the package:
```bash
python -m build
```

### Documentation

Generate documentation:
```bash
cd docs && make html
```

## Configuration

MambuPy requires configuration to connect to Mambu. Priority order (highest to lowest):

1. Command-line arguments: `--mambupy_apiurl`, `--mambupy_apiuser`, `--mambupy_apipwd`
2. Environment variables: `MAMBUPY_APIURL`, `MAMBUPY_APIUSER`, `MAMBUPY_APIPWD`
3. RC files: `~/.mambupy.rc` or `/etc/mambupy.rc`

RC file format:
```ini
[API]
apiurl=https://your-domain.mambu.com
apiuser=your_api_user
apipwd=your_api_password
apipagination=50
activate_request_session_objects=True

[DB]
dbname=database_name
dbuser=db_user
dbpwd=db_password
dbhost=db_host
dbport=3306
dbeng=mysql

[MAMBUPY]
loggingconf=path/to/logging/config.yaml
```

**Important**: When using argparse in programs that import MambuPy, use `parse_known_args()` instead of `parse_args()` to avoid conflicts with MambuPy's command-line arguments.

## Dependencies

Since v2.0.0, MambuPy uses `pyproject.toml` for dependency management.

### Installation Options

**Default Installation (REST API only)**
```bash
# Using pip
pip install MambuPy

# Using uv (recommended for faster installs)
uv pip install MambuPy
```
Includes: PyYAML, requests, requests_toolbelt, dateutils, future

**Full Installation (REST API + ORM)**
```bash
# Using pip
pip install MambuPy[full]

# Using uv
uv pip install MambuPy[full]
```
Additional: SQLAlchemy, mysqlclient

**Development Installation**
```bash
# Using pip
pip install MambuPy[dev]

# Using uv (installs dev dependencies in current environment)
uv pip install -e ".[dev]"
```
Includes: freezegun, mock, coverage, pylint, ruff, black, isort

**Documentation Build**
```bash
# Using pip
pip install MambuPy[doc]

# Using uv
uv pip install ".[doc]"
```

**Deployment Tools**
```bash
# Using pip
pip install MambuPy[deploy]

# Using uv
uv pip install ".[deploy]"
```

### Development Environment Setup with uv

```bash
# Create virtual environment and install with dev dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev,full]"
```

## Key Implementation Notes

### Session Management

Recent versions implement a Singleton pattern for HTTP sessions (`SessionSingleton` in `MambuPy/api/connector/rest.py`). This allows persistent TCP connections when `activate_request_session_objects=True` is configured.

### Retry Strategy

REST connector automatically retries failed requests (5 retries by default) for status codes: 429, 500, 502, 503, 504 with exponential backoff.

### Logging

MambuPy uses Python's logging module. Configure via YAML file specified in `loggingconf` config option. Logs propagate to parent loggers by default. **Important**: Logs avoid printing sensitive data (passwords, API keys).

### Error Handling

- `MambuError` - Errors from Mambu API responses
- `MambuCommError` - Communication errors with Mambu
- `MambuPyError` - General MambuPy exceptions

### Pagination

Default pagination limit is 50 items per request (configurable via `apipagination`). Use `OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE` constant for special pagination cases.

## Testing Notes

- Tests use `unittest` framework with `mock` for Mambu API responses
- Tests are split into:
  - Root level: REST v1 and common functionality tests
  - `tests/api/`: REST v2 specific tests
  - `tests/orm/`: ORM specific tests
- The `unit.sh` script can skip API v2 tests with `-a no` flag
- Coverage reports are generated with each test run

## Code Style

- Line length: 90 characters (black/isort configured)
- Import order: stdlib, third-party, local (enforced by isort)
- Single-line imports enforced then collapsed (isort workflow)
- Ruff checks enabled except E501 (line length, handled by black)

## Package Structure

The codebase has a symlink `mambupy -> MambuPy` for case-insensitive compatibility. The actual source code is in `MambuPy/` directory. A `CaseInsensitiveFinder` meta path finder is also implemented in `__init__.py` for import flexibility.
