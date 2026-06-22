import sqlite3
from typing import Dict, Any, Optional

from backend.memory._sqlite import connect as open_connection

class IdentityStore:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def init_db(self):
        with open_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    global_health REAL,
                    saturation_health REAL,
                    diversity_health REAL,
                    belief_health REAL,
                    recall_health REAL,
                    health_delta REAL,
                    confidence_score REAL,
                    system_state TEXT,
                    velocity_warning BOOLEAN
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    health_log_id INTEGER,
                    audit_type TEXT,
                    primary_driver TEXT,
                    driver_delta REAL,
                    recommended_circuit_breaker TEXT,
                    audit_confidence REAL,
                    FOREIGN KEY(health_log_id) REFERENCES health_logs(id)
                )
            ''')
            conn.commit()

    def log_health_report(self, metrics: Dict[str, Any], state: str, warning: bool) -> int:
        with open_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO health_logs (
                    global_health, saturation_health, diversity_health,
                    belief_health, recall_health, health_delta,
                    confidence_score, system_state, velocity_warning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics["global_health"], metrics["saturation_health"],
                metrics["diversity_health"], metrics["belief_health"],
                metrics["recall_health"], metrics["health_delta"],
                metrics["confidence_score"], state, warning
            ))
            conn.commit()
            return cursor.lastrowid

    def log_audit_artifact(self, health_log_id: int, artifact: Dict[str, Any]):
        with open_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_logs (
                    health_log_id, audit_type, primary_driver,
                    driver_delta, recommended_circuit_breaker, audit_confidence
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                health_log_id, artifact["audit_type"], artifact["primary_driver"],
                artifact["driver_delta"], artifact["recommended_circuit_breaker"],
                artifact["audit_confidence"]
            ))
            conn.commit()

    def get_latest_health(self) -> Optional[Dict[str, Any]]:
        with open_connection(self.db_path, row_factory=sqlite3.Row) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM health_logs ORDER BY timestamp DESC LIMIT 1')
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None