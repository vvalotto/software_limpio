"""
Sistema de snapshots y persistencia para ArchitectAnalyst.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent import ArchitectureSnapshot


class SnapshotStore:
    """
    Almacén de snapshots de arquitectura usando SQLite.
    """

    def __init__(self, db_path: Path):
        """
        Inicializa el almacén.

        Args:
            db_path: Ruta a la base de datos SQLite
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Inicializa el esquema de la base de datos."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    project_hash TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER NOT NULL,
                    violation_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
                )
            """)

            conn.commit()

    def save(self, snapshot: ArchitectureSnapshot) -> int:
        """
        Guarda un snapshot en la base de datos.

        Args:
            snapshot: Snapshot a guardar

        Returns:
            ID del snapshot guardado
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO snapshots (timestamp) VALUES (?)",
                (snapshot.timestamp.isoformat(),)
            )
            snapshot_id = cursor.lastrowid

            for name, value in snapshot.metrics.items():
                conn.execute(
                    "INSERT INTO metrics (snapshot_id, metric_name, metric_value) VALUES (?, ?, ?)",
                    (snapshot_id, name, value)
                )

            for violation in snapshot.violations:
                conn.execute(
                    "INSERT INTO violations (snapshot_id, violation_type, description) VALUES (?, ?, ?)",
                    (snapshot_id, "layer", violation)
                )

            conn.commit()

        assert snapshot_id is not None
        return snapshot_id

    def get_history(self, metric_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene histórico de una métrica.

        Args:
            metric_name: Nombre de la métrica
            limit: Número máximo de registros

        Returns:
            Lista de valores con timestamps
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT s.timestamp, m.metric_value
                FROM metrics m
                JOIN snapshots s ON m.snapshot_id = s.id
                WHERE m.metric_name = ?
                ORDER BY s.timestamp DESC
                LIMIT ?
            """, (metric_name, limit))

            return [
                {"timestamp": row[0], "value": row[1]}
                for row in cursor.fetchall()
            ]

    def get_latest(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el snapshot más reciente.

        Returns:
            Diccionario con el snapshot o None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, timestamp FROM snapshots
                ORDER BY timestamp DESC LIMIT 1
            """)
            row = cursor.fetchone()

            if not row:
                return None

            snapshot_id, timestamp = row

            # Obtener métricas
            cursor = conn.execute(
                "SELECT metric_name, metric_value FROM metrics WHERE snapshot_id = ?",
                (snapshot_id,)
            )
            metrics = {row[0]: row[1] for row in cursor.fetchall()}

            # Obtener violaciones
            cursor = conn.execute(
                "SELECT description FROM violations WHERE snapshot_id = ?",
                (snapshot_id,)
            )
            violations = [row[0] for row in cursor.fetchall()]

            return {
                "id": snapshot_id,
                "timestamp": timestamp,
                "metrics": metrics,
                "violations": violations,
            }
