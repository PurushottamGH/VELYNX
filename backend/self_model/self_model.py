import os
import json

from backend.self_model.baseline_tracker import BaselineTracker
from backend.self_model.health_monitor import CognitiveHealthMonitor
from backend.self_model.self_audit import CognitiveAuditor
from backend.self_model.identity_store import IdentityStore

def run_cognitive_cycle():
    # Initialize databases
    store = IdentityStore("velynx_identity.db")
    store.init_db()
    
    # Initialize components
    tracker = BaselineTracker()
    monitor = CognitiveHealthMonitor(total_ontology_concepts=100)
    auditor = CognitiveAuditor()
    
    # Get current metrics
    tracker_data = tracker.generate_tracker_aggregates()
    prev_health = store.get_latest_health()

    # Prepare previous health context
    prev_health_dict = None
    if prev_health:
        prev_health_dict = {
            "metrics": prev_health,
            "system_state": prev_health.get("system_state"),
            "velocity_warning": prev_health.get("velocity_warning", False)
        }
    
    # Generate health report
    health_report = monitor.generate_health_report(
        memory_count=tracker_data.get("memory_count", 0),
        saturation_ratio=tracker_data.get("saturation_ratio", 0.0),
        unique_concepts_seen=tracker_data.get("unique_concepts_seen", 0),
        entropy_score=tracker_data.get("entropy_score", 0.0),
        prediction_friction=tracker_data.get("prediction_friction", 0.0),
        input_energy=tracker_data.get("input_energy", 0.0),
        recall_energy=tracker_data.get("recall_energy", "unsupported"),
        previous_global_health=prev_health["global_health"] if prev_health else None
    )
    
    # Run audit system
    audit_artifact = auditor.run_audit(health_report, prev_health_dict, tracker_data)

    # Store results
    log_id = store.log_health_report(
        health_report["metrics"],
        health_report["system_state"],
        health_report.get("velocity_warning", False)
    )
    store.log_audit_artifact(log_id, audit_artifact)

    # Final diagnostic output
    print("\n--- VELYNX COGNITIVE CYCLE COMPLETE ---")
    print(f"HEALTH STATE: {health_report['system_state']}")
    print(f"GLOBAL HEALTH: {health_report['metrics']['global_health']:.4f}")
    print("\nAUDIT ARTIFACT:")
    print(json.dumps(audit_artifact, indent=2))

if __name__ == "__main__":
    run_cognitive_cycle()