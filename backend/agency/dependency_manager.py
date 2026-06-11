from __future__ import annotations

import logging
import re
import subprocess
import sys
from typing import Any

logger = logging.getLogger(__name__)

MODULE_NOT_FOUND_PATTERN = re.compile(
    r"ModuleNotFoundError:\s+No module named\s+['\"]([^'\"]+)['\"]"
)
IMPORT_ERROR_PATTERN = re.compile(
    r"ImportError:\s+No module named\s+['\"]([^'\"]+)['\"]"
)


class DependencyManager:
    def extract_missing_package(self, error_message: str) -> str | None:
        match = MODULE_NOT_FOUND_PATTERN.search(error_message)
        if match:
            return match.group(1)
        match = IMPORT_ERROR_PATTERN.search(error_message)
        if match:
            return match.group(1)
        return None

    def install_package(self, package_name: str) -> bool:
        logger.info("Attempting to install package: %s", package_name)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
        except subprocess.TimeoutExpired:
            logger.error("Installation timed out for package: %s", package_name)
            return False
        except FileNotFoundError:
            logger.error("pip not found for package: %s", package_name)
            return False
        except PermissionError:
            logger.error("Permission denied installing package: %s", package_name)
            return False
        except OSError as exc:
            logger.error("OS error installing package %s: %s", package_name, exc)
            return False

        if result.returncode == 0:
            logger.info("Successfully installed package: %s", package_name)
            return True

        logger.error(
            "Failed to install package %s: %s",
            package_name,
            result.stderr.strip() or "Unknown error",
        )
        return False

    def resolve_dependencies(self, qa_report: dict[str, Any]) -> dict[str, Any]:
        test_output = qa_report.get("test_output", "")
        if not isinstance(test_output, str):
            return {"resolved": False, "package": None}

        missing_package = self.extract_missing_package(test_output)
        if not missing_package:
            return {"resolved": False, "package": None}

        success = self.install_package(missing_package)
        return {"resolved": success, "package": missing_package}
