"""Script to update and rotate Home Assistant demo blueprints for Blueprints Updater.

This script manages a 4-day deterministic simulation cycle:
- Phase 1: Changes `motion_sensor` selector `device_class` to `occupancy` (breaking update).
- Phase 2: Safe update (keeps `occupancy`, updates `update_id` and timestamp).
- Phase 3: Changes `motion_sensor` selector `device_class` to `motion` (breaking update).
- Phase 4: Safe update (keeps `motion`, updates `update_id` and timestamp).
"""

import os
import re
import sys
import uuid
from datetime import datetime, timezone

PHASES = {
    1: {
        "device_class": "occupancy",
        "name": "Phase 1/4: Changed device_class to occupancy",
        "type": "breaking_change",
    },
    2: {
        "device_class": "occupancy",
        "name": "Phase 2/4: Safe update (device_class: occupancy)",
        "type": "safe_update",
    },
    3: {
        "device_class": "motion",
        "name": "Phase 3/4: Changed device_class to motion",
        "type": "breaking_change",
    },
    4: {
        "device_class": "motion",
        "name": "Phase 4/4: Safe update (device_class: motion)",
        "type": "safe_update",
    },
}

MANUAL_MAP = {
    "occupancy_change": 1,
    "occupancy_safe": 2,
    "motion_change": 3,
    "motion_safe": 4,
}


def get_phase(mode: str) -> int:
    """Determine the active simulation phase number.

    Args:
        mode: The requested mode ('auto', a manual alias like 'occupancy_change',
            or a numeric phase string).

    Returns:
        The phase integer (1 through 4).

    """
    if mode in MANUAL_MAP:
        return MANUAL_MAP[mode]
    if mode.isdigit() and int(mode) in PHASES:
        return int(mode)

    # Auto: Deterministic 4-day rotation based on epoch days
    epoch_days = int(datetime.now(timezone.utc).timestamp() // 86400)
    return (epoch_days % 4) + 1


def update_blueprint(file_path: str, mode: str = "auto") -> None:
    """Update blueprint file with current phase device_class, UUID, and timestamp.

    Args:
        file_path: Path to the blueprint YAML file.
        mode: Simulation mode ('auto' or specific phase key).

    Raises:
        FileNotFoundError: If the target blueprint file does not exist.

    """
    phase_num = get_phase(mode)
    phase_info = PHASES[phase_num]
    target_device_class = phase_info["device_class"]
    phase_title = phase_info["name"]

    new_uuid = str(uuid.uuid4())
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target file '{file_path}' does not exist.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Update device_class under motion_sensor selector
    content = re.sub(
        r"(device_class:\s*)(motion|occupancy)", rf"\g<1>{target_device_class}", content
    )

    # Update update_id
    content = re.sub(r"(update_id:\s*)[^\n]+", rf"\g<1>{new_uuid}", content)

    # Update last_updated
    content = re.sub(r"(last_updated:\s*)[^\n]+", rf'\g<1>"{current_time}"', content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Updated {file_path}")
    print(f"Phase: {phase_title}")
    print(f"Device Class: {target_device_class}")
    print(f"Update ID: {new_uuid}")
    print(f"Last Updated: {current_time}")

    commit_title = f"Update blueprints [{phase_title}]"
    commit_body = f"- {file_path}: {new_uuid} ({current_time})\n- device_class: {target_device_class}\n- simulation_phase: {phase_title}"

    # Export variables if running in GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"COMMIT_TITLE={commit_title}\n")
            f.write(f"PHASE_NAME={phase_title}\n")
            f.write(f"DEVICE_CLASS={target_device_class}\n")
            f.write(f"UPDATE_ID={new_uuid}\n")
            f.write(f"LAST_UPDATED={current_time}\n")
            f.write("COMMIT_BODY<<EOF\n")
            f.write(f"{commit_body}\n")
            f.write("EOF\n")


def main() -> None:
    """Execute the blueprint update CLI entry point."""
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "auto"
    file_arg = (
        sys.argv[2] if len(sys.argv) > 2 else "blueprints/motion_light_blueprint.yaml"
    )
    update_blueprint(file_arg, mode_arg)


if __name__ == "__main__":
    main()
