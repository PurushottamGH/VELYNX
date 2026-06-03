#!/usr/bin/env python3
"""
VELYNX CORE v2 - Installation Verification Script
"""

import sys
import os
from pathlib import Path

def verify_installation():
    """Verify that VELYNX CORE v2 is properly installed."""
    print("Verifying VELYNX CORE v2 installation...")

    # Check if required files exist
    required_files = [
        "velynx_core/__init__.py",
        "velynx_core/memory.py",
        "velynx_core/brain.py",
        "velynx_core/learner.py",
        "velynx_core/self_coder.py",
        "velynx_core/velynx.py",
        "test_velynx_core.py"
    ]

    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Missing required file: {file}")
            return False
        print(f"✅ Found {file}")

    # Check if dependencies can be imported
    try:
        import numpy
        print("✅ numpy import successful")
    except ImportError:
        print("❌ numpy import failed")
        return False

    try:
        import git
        print("✅ gitpython import successful")
    except ImportError:
        print("❌ gitpython import failed")
        return False

    try:
        import sentence_transformers
        print("✅ sentence-transformers import successful")
    except ImportError:
        print("❌ sentence-transformers import failed")
        return False

    # Try importing velynx modules
    try:
        sys.path.insert(0, ".")
        from velynx_core import __version__
        print(f"✅ VELYNX CORE v2 version {__version__} import successful")
    except Exception as e:
        print(f"❌ VELYNX CORE v2 import failed: {e}")
        return False

    # Test instantiation
    try:
        from velynx_core.memory import VelynxMemory, Concept
        from velynx_core.brain import VelynxBrain
        from velynx_core.learner import VelynxLearner
        from velynx_core.velynx import VelynxSystem

        # Test with temporary database
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            memory = VelynxMemory(db_path)
            brain = VelynxBrain(memory)
            learner = VelynxLearner(memory)
            memory.close()

        print("✅ VELYNX components instantiated successfully")
    except Exception as e:
        print(f"❌ VELYNX component instantiation failed: {e}")
        return False

    print("\n🎉 VELYNX CORE v2 installation verified successfully!")
    return True

if __name__ == "__main__":
    if verify_installation():
        print("\nYou can now run VELYNX with:")
        print("  python -m velynx_core.velynx")
        print("  # or")
        print("  python velynx_core/velynx.py")
    else:
        print("\n❌ Installation verification failed!")
        sys.exit(1)