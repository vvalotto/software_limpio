"""
Sistema de snapshots y persistencia para ArchitectAnalyst.

Persiste los resultados de cada análisis en SQLite para permitir comparación
de tendencias entre sprints. Cada ejecución de `architectanalyst` guarda un
snapshot con todos los ArchitectureResult del análisis.

Ticket: 4.1 — Refactorizar SnapshotStore para usar ArchitectureResult
Fecha: 2026-03-01
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity


class SnapshotStore:
    """
    Almacén de snapshots de arquitectura usando SQLite.

    Esquema:
        snapshots(id, timestamp, sprint_id, project_path)
        results(id, snapshot_id, analyzer_name, metric_name, module_path,
                value, threshold, severity, message)

    Cada snapshot corresponde a una ejecución completa de ArchitectAnalyst.
    Los resultados se guardan sin el campo `trend` — este se calcula en tiempo
    de ejecución comparando con el snapshot anterior vía TrendCalculator.

    Attributes:
        db_path: Ruta al archivo SQLite.
    """

    def __init__(self, db_path: Path) -> None:
        """
        Inicializa el almacén y crea/migra el esquema.

        Args:
            db_path: Ruta al archivo SQLite (se crea si no existe).
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Inicializa o migra el esquema de la base de datos."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            existing = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }

            # Migración desde esquema legacy del skeleton (tenía 'metrics' y 'violations')
            if "metrics" in existing and "results" not in existing:
                conn.execute("DROP TABLE IF EXISTS violations")
                conn.execute("DROP TABLE IF EXISTS metrics")
                conn.execute("DROP TABLE IF EXISTS snapshots")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp   TEXT    NOT NULL,
                    sprint_id   TEXT,
                    project_path TEXT   NOT NULL DEFAULT ''
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id   INTEGER NOT NULL,
                    analyzer_name TEXT    NOT NULL,
                    metric_name   TEXT    NOT NULL,
                    module_path   TEXT    NOT NULL,
                    value         REAL    NOT NULL,
                    threshold     REAL,
                    severity      TEXT    NOT NULL,
                    message       TEXT    NOT NULL,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
                )
            """)

            conn.commit()

    # -------------------------------------------------------------------------
    # Escritura
    # -------------------------------------------------------------------------

    def save(
        self,
        results: List[ArchitectureResult],
        sprint_id: Optional[str] = None,
        project_path: str = "",
    ) -> int:
        """
        Persiste un snapshot completo en la base de datos.

        Args:
            results: Lista de ArchitectureResult del análisis actual.
            sprint_id: Identificador del sprint (ej: "sprint-12"). Opcional.
            project_path: Ruta del proyecto analizado. Opcional.

        Returns:
            ID del snapshot guardado.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO snapshots (timestamp, sprint_id, project_path) VALUES (?, ?, ?)",
                (timestamp, sprint_id, project_path),
            )
            snapshot_id = cursor.lastrowid
            assert snapshot_id is not None

            for result in results:
                conn.execute(
                    """INSERT INTO results
                       (snapshot_id, analyzer_name, metric_name, module_path,
                        value, threshold, severity, message)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        snapshot_id,
                        result.analyzer_name,
                        result.metric_name,
                        str(result.module_path),
                        result.value,
                        result.threshold,
                        result.severity.value,
                        result.message,
                    ),
                )

            conn.commit()

        return snapshot_id

    # -------------------------------------------------------------------------
    # Lectura
    # -------------------------------------------------------------------------

    def get_latest_results(self) -> Optional[List[ArchitectureResult]]:
        """
        Retorna los ArchitectureResult del snapshot más reciente.

        Returns:
            Lista de resultados, o None si no hay snapshots guardados.
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT id FROM snapshots ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()

            if row is None:
                return None

            snapshot_id = row[0]
            return self._load_results(conn, snapshot_id)

    def get_snapshot_count(self) -> int:
        """Retorna el número total de snapshots almacenados."""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]

    # -------------------------------------------------------------------------
    # Helpers privados
    # -------------------------------------------------------------------------

    def _load_results(
        self, conn: sqlite3.Connection, snapshot_id: int
    ) -> List[ArchitectureResult]:
        """Carga los resultados de un snapshot desde la DB."""
        rows = conn.execute(
            """SELECT analyzer_name, metric_name, module_path,
                      value, threshold, severity, message
               FROM results WHERE snapshot_id = ?""",
            (snapshot_id,),
        ).fetchall()

        results = []
        for row in rows:
            analyzer_name, metric_name, module_path, value, threshold, severity_str, message = row
            results.append(ArchitectureResult(
                analyzer_name=analyzer_name,
                metric_name=metric_name,
                module_path=Path(module_path),
                value=value,
                threshold=threshold,
                severity=ArchitectureSeverity(severity_str),
                message=message,
                trend=None,
            ))

        return results
