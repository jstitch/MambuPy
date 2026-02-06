#!/usr/bin/env python3
"""Update user roles from a CSV file.

This script reads a CSV file containing usernames and role identifiers, validates
the data, and updates user roles in Mambu accordingly.

CSV Format:
    The CSV file should contain at least two columns: username and role.
    - Lines starting with '#' are treated as comments and ignored
    - Extra columns are allowed but will be ignored
    - The file can have a header row (will be validated like any other row)
    - Role can be specified by name OR by ID

Example CSV:
    username,role
    john.doe,Credit Officer
    jane.smith,BRANCH_MANAGER_ID
    # This is a comment line
    bob.johnson,Accountant

Requirements:
    - All specified roles must exist in Mambu (validated at startup)
    - Roles can be identified by name or ID
    - Users that don't exist will be skipped with a warning
    - The script uses detailsLevel="FULL" for comprehensive data retrieval

Usage:
    python update_user_roles.py users_roles.csv

    With custom CSV format:
    python update_user_roles.py users_roles.csv --username-col 0 --role-col 1

Author: MambuPy Contributors
License: Apache 2.0
"""

import argparse
import csv
import logging
import sys
from typing import Dict, List, Tuple, Set

from mambupy.api.mambuuser import MambuUser
from mambupy.api.mamburole import MambuRole
from mambupy.mambuutil import MambuError, MambuPyError, setup_logging


# Configure logging
logger = setup_logging(__name__)


class UserRoleUpdater:
    """Handles the process of updating user roles from a CSV file."""

    def __init__(self, csv_file: str, username_col: int = 0, role_col: int = 1,
                 delimiter: str = ',', dry_run: bool = False):
        """Initialize the UserRoleUpdater.

        Args:
            csv_file: Path to the CSV file containing username and role data
            username_col: Zero-indexed column number for usernames (default: 0)
            role_col: Zero-indexed column number for roles (default: 1)
            delimiter: CSV delimiter character (default: ',')
            dry_run: If True, validate but don't actually update users
        """
        self.csv_file = csv_file
        self.username_col = username_col
        self.role_col = role_col
        self.delimiter = delimiter
        self.dry_run = dry_run
        self.roles_cache: Dict[str, MambuRole] = {}  # Cache by name OR id
        self.stats = {
            'processed': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'comments': 0
        }

    def validate_roles(self, role_identifiers: Set[str]) -> bool:
        """Validate that all specified roles exist in Mambu.

        This method retrieves all roles from Mambu and checks that each role
        identifier (name OR id) specified in the CSV exists. It also caches
        the role objects for later use during updates.

        Args:
            role_identifiers: Set of role names or IDs to validate

        Returns:
            True if all roles exist, False otherwise

        Raises:
            MambuError: If there's an error communicating with Mambu
            MambuPyError: If there's a general MambuPy error
        """
        logger.info("Retrieving all roles from Mambu for validation...")

        try:
            all_roles = MambuRole.get_all(detailsLevel="FULL")
        except (MambuError, MambuPyError) as e:
            logger.error(f"Failed to retrieve roles from Mambu: {e}")
            raise

        # Build cache of role name/id -> role object
        # Store by both name AND id so either can be used for lookup
        for role in all_roles:
            role_name = role._attrs.get('name')
            role_id = role._attrs.get('id')

            if role_name:
                self.roles_cache[role_name] = role
            if role_id:
                self.roles_cache[role_id] = role

        logger.info(f"Found {len(all_roles)} roles in Mambu")

        # Check if all requested roles exist
        missing_roles = role_identifiers - set(self.roles_cache.keys())

        if missing_roles:
            logger.error("The following roles do not exist in Mambu:")
            for role in sorted(missing_roles):
                logger.error(f"  - {role}")
            return False

        logger.info("All specified roles validated successfully")
        return True

    def parse_csv(self) -> List[Tuple[str, str]]:
        """Parse the CSV file and extract username-role pairs.

        Processes the CSV file, ignoring comment lines (starting with '#') and
        extracting username and role identifier (name or ID) from the specified columns.

        Returns:
            List of (username, role_identifier) tuples

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV format is invalid
        """
        user_role_pairs = []

        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=self.delimiter)

                for line_num, row in enumerate(reader, start=1):
                    # Skip empty lines
                    if not row or not any(row):
                        continue

                    # Skip comment lines
                    if row[0].strip().startswith('#'):
                        self.stats['comments'] += 1
                        logger.debug(f"Line {line_num}: Skipping comment")
                        continue

                    # Validate that the row has enough columns
                    required_cols = max(self.username_col, self.role_col) + 1
                    if len(row) < required_cols:
                        logger.warning(
                            f"Line {line_num}: Insufficient columns "
                            f"(found {len(row)}, need {required_cols}). Skipping."
                        )
                        self.stats['skipped'] += 1
                        continue

                    # Extract username and role identifier (name or ID)
                    username = row[self.username_col].strip()
                    role_identifier = row[self.role_col].strip()

                    # Skip if either field is empty
                    if not username or not role_identifier:
                        logger.warning(
                            f"Line {line_num}: Empty username or role. Skipping."
                        )
                        self.stats['skipped'] += 1
                        continue

                    user_role_pairs.append((username, role_identifier))
                    logger.debug(
                        f"Line {line_num}: Found user '{username}' -> role '{role_identifier}'"
                    )

        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_file}")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise ValueError(f"Invalid CSV format: {e}")

        logger.info(
            f"Parsed CSV: {len(user_role_pairs)} user-role pairs, "
            f"{self.stats['comments']} comments, "
            f"{self.stats['skipped']} invalid rows"
        )

        return user_role_pairs

    def update_user_role(self, username: str, role_identifier: str) -> bool:
        """Update a single user's role.

        Retrieves the user from Mambu, updates their role, and patches the
        changes back to Mambu.

        Args:
            username: The username to update
            role_identifier: The new role name or ID to assign

        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Retrieve the user
            logger.debug(f"Retrieving user: {username}")
            user = MambuUser().get(username, detailsLevel="FULL")

            # Get the role object from cache (works with name OR id)
            new_role = self.roles_cache[role_identifier]
            new_role_name = new_role._attrs.get('name', 'N/A')
            new_role_id = new_role._attrs.get('id', 'N/A')

            # Check if user already has this role (compare by encodedKey for accuracy)
            current_role_key = user._attrs.get('role', {}).get('encodedKey')
            new_role_key = new_role._attrs.get('encodedKey')

            if current_role_key == new_role_key:
                logger.info(
                    f"User '{username}' already has role '{new_role_name}' ({new_role_id}). "
                    "No update needed."
                )
                return True

            current_role_name = user._attrs.get('role', {}).get('name', 'N/A')
            logger.info(
                f"Updating user '{username}': '{current_role_name}' -> '{new_role_name}' ({new_role_id})"
            )

            if not self.dry_run:
                # Update the role in the user object
                user._attrs['role'] = {
                    'encodedKey': new_role._attrs['encodedKey'],
                    'id': new_role._attrs['id']
                }

                # Patch the user to Mambu
                user.patch(['role'])
                logger.info(f"Successfully updated user '{username}'")
            else:
                logger.info(f"[DRY RUN] Would update user '{username}'")

            return True

        except MambuError as e:
            if "INVALID_PARAMETERS" in str(e) or "NOT_FOUND" in str(e):
                logger.warning(f"User '{username}' not found in Mambu. Skipping.")
            else:
                logger.error(f"Mambu error updating user '{username}': {e}")
            return False

        except MambuPyError as e:
            logger.error(f"MambuPy error updating user '{username}': {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error updating user '{username}': {e}")
            return False

    def process(self) -> int:
        """Process the CSV file and update all user roles.

        This is the main processing method that:
        1. Parses the CSV file
        2. Validates all roles exist
        3. Updates each user's role

        Returns:
            0 if successful, 1 if there were errors

        Raises:
            SystemExit: If role validation fails
        """
        # Parse CSV
        try:
            user_role_pairs = self.parse_csv()
        except Exception as e:
            logger.error(f"Failed to parse CSV: {e}")
            return 1

        if not user_role_pairs:
            logger.warning("No valid user-role pairs found in CSV file")
            return 0

        # Extract unique role identifiers for validation
        unique_roles = {role_identifier for _, role_identifier in user_role_pairs}
        logger.info(f"Found {len(unique_roles)} unique roles to validate")

        # Validate all roles exist
        try:
            if not self.validate_roles(unique_roles):
                logger.error(
                    "Role validation failed. Please ensure all roles exist in Mambu."
                )
                return 1
        except Exception as e:
            logger.error(f"Role validation error: {e}")
            return 1

        # Process each user
        logger.info(f"Processing {len(user_role_pairs)} user updates...")

        for username, role_identifier in user_role_pairs:
            self.stats['processed'] += 1

            if self.update_user_role(username, role_identifier):
                self.stats['updated'] += 1
            else:
                self.stats['errors'] += 1

        # Print summary
        self._print_summary()

        return 0 if self.stats['errors'] == 0 else 1

    def _print_summary(self):
        """Print a summary of the processing results."""
        logger.info("=" * 60)
        logger.info("PROCESSING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total rows processed:  {self.stats['processed']}")
        logger.info(f"Successfully updated:  {self.stats['updated']}")
        logger.info(f"Errors:                {self.stats['errors']}")
        logger.info(f"Comments skipped:      {self.stats['comments']}")
        logger.info(f"Invalid rows skipped:  {self.stats['skipped']}")
        logger.info("=" * 60)

        if self.dry_run:
            logger.info("DRY RUN MODE: No actual changes were made to Mambu")


def main():
    """Main entry point for the CLI script."""
    parser = argparse.ArgumentParser(
        description='Update user roles in Mambu from a CSV file.',
        epilog='''
Examples:
  %(prog)s users_roles.csv
  %(prog)s users_roles.csv --dry-run
  %(prog)s users_roles.csv --username-col 0 --role-col 2
  %(prog)s users_roles.csv --delimiter ";" --verbose

CSV Format:
  The CSV file should contain at least two columns with username and role.
  Roles can be specified by NAME or by ID.
  Lines starting with '#' are treated as comments.

  Example:
    username,role
    john.doe,Credit Officer
    jane.smith,BRANCH_MANAGER_ID
    # This user is on leave
    bob.johnson,Accountant
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'csv_file',
        help='Path to CSV file containing username and role columns'
    )

    parser.add_argument(
        '--username-col',
        type=int,
        default=0,
        metavar='N',
        help='Zero-indexed column number for usernames (default: 0)'
    )

    parser.add_argument(
        '--role-col',
        type=int,
        default=1,
        metavar='N',
        help='Zero-indexed column number for roles (default: 1)'
    )

    parser.add_argument(
        '--delimiter',
        type=str,
        default=',',
        metavar='CHAR',
        help='CSV delimiter character (default: ",")'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate data but do not actually update users in Mambu'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )

    # Use parse_known_args to avoid conflicts with MambuPy's CLI args
    args, _ = parser.parse_known_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    # Create updater and process
    updater = UserRoleUpdater(
        csv_file=args.csv_file,
        username_col=args.username_col,
        role_col=args.role_col,
        delimiter=args.delimiter,
        dry_run=args.dry_run
    )

    return updater.process()


if __name__ == "__main__":
    sys.exit(main())
