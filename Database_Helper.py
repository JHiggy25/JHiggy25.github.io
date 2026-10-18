from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
from pathlib import Path
from typing import Any


PBKDF2_ITERATIONS = 600_000


def _hash_password(password: str, salt: bytes | None = None) -> str:
    """Create a salted PBKDF2-SHA256 password hash."""
    if salt is None:
        salt = secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    return (
        f"pbkdf2_sha256${PBKDF2_ITERATIONS}"
        f"${salt.hex()}${digest.hex()}"
    )


def _verify_password(password: str, stored_value: str) -> bool:
    """Verify a password hash or recognize a legacy plaintext password."""
    if stored_value.startswith("pbkdf2_sha256$"):
        try:
            _, iterations_text, salt_hex, digest_hex = stored_value.split("$", 3)
            iterations = int(iterations_text)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)

            actual = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                iterations,
            )
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

    # Compatibility with accounts created by the original starter project.
    # A successful login upgrades the plaintext password to a salted hash.
    return hmac.compare_digest(stored_value, password)


class DatabaseHelper:
    """Manage a local SQLite database, user accounts, and inventory."""

    def __init__(self) -> None:
        configured_path = os.getenv("INVENTORY_DB_PATH", "inventory.db")
        self.database_path = str(Path(configured_path).expanduser())
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Create required tables and migrate older inventory schemas."""
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    password TEXT NOT NULL
                )
                """
            )

            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    itemName TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    quantity INTEGER NOT NULL DEFAULT 0
                        CHECK (quantity >= 0),
                    low_stock_threshold INTEGER NOT NULL DEFAULT 3
                        CHECK (low_stock_threshold >= 0)
                )
                """
            )

            # Add the threshold column to an older inventory table if needed.
            columns = {
                row["name"]
                for row in self.connection.execute(
                    "PRAGMA table_info(inventory)"
                ).fetchall()
            }

            if "low_stock_threshold" not in columns:
                self.connection.execute(
                    """
                    ALTER TABLE inventory
                    ADD COLUMN low_stock_threshold INTEGER NOT NULL DEFAULT 3
                    """
                )

    # ---------------------------------------------------------
    # USER AUTHENTICATION
    # ---------------------------------------------------------

    def login_user(self, username: str, password: str) -> bool:
        """Return True when the username and password are valid."""
        username = username.strip()
        if not username or not password:
            return False

        row = self.connection.execute(
            """
            SELECT id, username, password
            FROM users
            WHERE username = ?
            LIMIT 1
            """,
            (username,),
        ).fetchone()

        if row is None or not _verify_password(password, row["password"]):
            return False

        if not row["password"].startswith("pbkdf2_sha256$"):
            with self.connection:
                self.connection.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (_hash_password(password), row["id"]),
                )

        return True

    def register_user(self, username: str, password: str) -> bool:
        """Register a new user with a securely hashed password."""
        username = username.strip()

        if not username or len(username) > 100 or len(password) < 8:
            return False

        try:
            with self.connection:
                self.connection.execute(
                    """
                    INSERT INTO users (username, password)
                    VALUES (?, ?)
                    """,
                    (username, _hash_password(password)),
                )
            return True
        except sqlite3.IntegrityError:
            # The username already exists, or another integrity rule failed.
            return False

    # ---------------------------------------------------------
    # INVENTORY RETRIEVAL
    # ---------------------------------------------------------

    def get_all_items(self) -> list[dict[str, Any]]:
        """Return inventory records ordered by item name."""
        rows = self.connection.execute(
            """
            SELECT id, itemName, quantity, low_stock_threshold
            FROM inventory
            ORDER BY itemName COLLATE NOCASE
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def get_item(self, item_name: str) -> dict[str, Any] | None:
        """Return one inventory record, or None if it does not exist."""
        item_name = item_name.strip()
        if not item_name:
            return None

        row = self.connection.execute(
            """
            SELECT id, itemName, quantity, low_stock_threshold
            FROM inventory
            WHERE itemName = ?
            LIMIT 1
            """,
            (item_name,),
        ).fetchone()
        return dict(row) if row is not None else None

    # ---------------------------------------------------------
    # INVENTORY CREATION
    # ---------------------------------------------------------

    def add_item(
        self,
        item_name: str,
        quantity: int,
        low_stock_threshold: int = 3,
    ) -> bool:
        """Add an item and its low-stock alert threshold."""
        item_name = item_name.strip()

        if not item_name or len(item_name) > 255:
            return False
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity < 0
        ):
            return False
        if (
            isinstance(low_stock_threshold, bool)
            or not isinstance(low_stock_threshold, int)
            or low_stock_threshold < 0
        ):
            return False

        try:
            with self.connection:
                self.connection.execute(
                    """
                    INSERT INTO inventory
                        (itemName, quantity, low_stock_threshold)
                    VALUES (?, ?, ?)
                    """,
                    (item_name, quantity, low_stock_threshold),
                )
            return True
        except sqlite3.IntegrityError:
            # Most commonly, an item with that name already exists.
            return False

    # ---------------------------------------------------------
    # INVENTORY UPDATES
    # ---------------------------------------------------------

    def update_item(self, item_name: str, quantity: int) -> bool:
        """Set an item's quantity; zero represents sold-out inventory."""
        item_name = item_name.strip()

        if not item_name:
            return False
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity < 0
        ):
            return False

        with self.connection:
            cursor = self.connection.execute(
                "UPDATE inventory SET quantity = ? WHERE itemName = ?",
                (quantity, item_name),
            )
        return cursor.rowcount > 0

    def set_item_threshold(self, item_name: str, threshold: int) -> bool:
        """Set the quantity at which a low-stock alert is triggered."""
        item_name = item_name.strip()

        if not item_name:
            return False
        if (
            isinstance(threshold, bool)
            or not isinstance(threshold, int)
            or threshold < 0
        ):
            return False

        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE inventory
                SET low_stock_threshold = ?
                WHERE itemName = ?
                """,
                (threshold, item_name),
            )
        return cursor.rowcount > 0

    # ---------------------------------------------------------
    # INVENTORY DELETION
    # ---------------------------------------------------------

    def delete_item(self, item_name: str) -> bool:
        """Delete an inventory item by name."""
        item_name = item_name.strip()
        if not item_name:
            return False

        with self.connection:
            cursor = self.connection.execute(
                "DELETE FROM inventory WHERE itemName = ?",
                (item_name,),
            )
        return cursor.rowcount > 0

    # ---------------------------------------------------------
    # STOCK ALERTS
    # ---------------------------------------------------------

    def get_low_stock_items(self) -> list[dict[str, Any]]:
        """Return items at or below their low-stock threshold."""
        rows = self.connection.execute(
            """
            SELECT id, itemName, quantity, low_stock_threshold
            FROM inventory
            WHERE quantity <= low_stock_threshold
            ORDER BY quantity ASC, itemName COLLATE NOCASE
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def get_out_of_stock_items(self) -> list[dict[str, Any]]:
        """Return items whose quantity is zero."""
        rows = self.connection.execute(
            """
            SELECT id, itemName, quantity, low_stock_threshold
            FROM inventory
            WHERE quantity = 0
            ORDER BY itemName COLLATE NOCASE
            """
        ).fetchall()
        return [dict(row) for row in rows]

    # ---------------------------------------------------------
    # CONNECTION MANAGEMENT
    # ---------------------------------------------------------

    def close(self) -> None:
        """Close the SQLite connection."""
        connection = getattr(self, "connection", None)
        if connection is not None:
            connection.close()
            self.connection = None

