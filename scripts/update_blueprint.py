"""Script to update and rotate Home Assistant demo blueprints for Blueprints Updater.

This script manages a 4-day deterministic simulation cycle:
- Phase 1: Changes `motion_sensor` selector `device_class` to `occupancy` (breaking update).
- Phase 2: Safe update (keeps `occupancy`, updates `update_id` and timestamp).
- Phase 3: Changes `motion_sensor` selector `device_class` to `motion` (breaking update).
- Phase 4: Safe update (keeps `motion`, updates `update_id` and timestamp).
"""

import argparse
import os
import re
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path

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

BLUEPRINT_SUMMARY = (
    "A simple blueprint that turns on a light or switch when motion is detected and turns "
    "it off when motion stops. This file is updated frequently to simulate new releases."
)

DEVICE_CLASS_PATTERN = re.compile(r"(?m)^(          device_class:[ \t]*)(motion|occupancy)[ \t]*$")
UPDATE_ID_PATTERN = re.compile(r"(?m)^(  update_id:\s*)[^\r\n]+$")
LAST_UPDATED_PATTERN = re.compile(r"(?m)^(  last_updated:\s*)[^\r\n]+$")
DESCRIPTION_PATTERN = re.compile(r"(?ms)^  description:.*?(?=^  author:)")


def build_description(phase_title: str, device_class: str, update_id: str, updated_at: str) -> str:
    """Build the blueprint description and its single current changelog entry."""
    return (
        "  description: |-\n"
        f"    {BLUEPRINT_SUMMARY}\n"
        "\n"
        "    Changelog:\n"
        f"    - {phase_title}\n"
        f"      device_class: {device_class}\n"
        f"      update_id: {update_id}\n"
        f"      updated: {updated_at}"
    )


def replace_description(content: str, description: str) -> str:
    """Replace the top-level blueprint description, including any old changelog."""
    replacement = f"{description}\n"
    updated_content, replacements = DESCRIPTION_PATTERN.subn(replacement, content, count=1)
    if replacements != 1:
        raise ValueError("Could not find the top-level blueprint description.")
    return updated_content


def get_phase(mode: str) -> int:
    """Determine the active simulation phase number.

    Args:
        mode: The requested mode ('auto', a manual alias like 'occupancy_change',
            or a numeric phase string).

    Returns:
        The phase integer (1 through 4).

    """
    if mode == "auto":
        epoch_days = int(datetime.now(UTC).timestamp() // 86400)
        return (epoch_days % 4) + 1
    if mode in MANUAL_MAP:
        return MANUAL_MAP[mode]
    if mode.isdigit() and int(mode) in PHASES:
        return int(mode)
    raise ValueError(f"Invalid mode '{mode}'. Use auto, 1-4, or a manual phase alias.")


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
    current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    target_path = Path(file_path)
    try:
        with target_path.open(encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Target file '{file_path}' does not exist.") from exc

    content, replacements = DEVICE_CLASS_PATTERN.subn(
        rf"\g<1>{target_device_class}", content, count=1
    )
    if replacements != 1:
        raise ValueError("Could not find the motion_sensor device_class selector.")

    content, replacements = UPDATE_ID_PATTERN.subn(rf"\g<1>{new_uuid}", content, count=1)
    if replacements != 1:
        raise ValueError("Could not find the blueprint update_id variable.")

    content, replacements = LAST_UPDATED_PATTERN.subn(rf'\g<1>"{current_time}"', content, count=1)
    if replacements != 1:
        raise ValueError("Could not find the blueprint last_updated variable.")

    # Replace the previous changelog in the top-level blueprint description.
    description = build_description(phase_title, target_device_class, new_uuid, current_time)
    content = replace_description(content, description)

    target_path = target_path.resolve()
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=target_path.parent,
            prefix=f".{target_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as f:
            temp_path = Path(f.name)
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, target_path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    print(f"Updated {file_path}")
    print(f"Phase: {phase_title}")
    print(f"Device Class: {target_device_class}")
    print(f"Update ID: {new_uuid}")
    print(f"Last Updated: {current_time}")

    commit_title = f"Update blueprints [{phase_title}]"
    commit_body = (
        f"- {file_path}: {new_uuid} ({current_time})\n"
        f"- device_class: {target_device_class}\n"
        f"- simulation_phase: {phase_title}"
    )

    if github_output := os.environ.get("GITHUB_OUTPUT"):
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"COMMIT_TITLE={commit_title}\n")
            f.write(f"PHASE_NAME={phase_title}\n")
            f.write(f"DEVICE_CLASS={target_device_class}\n")
            f.write(f"UPDATE_ID={new_uuid}\n")
            f.write(f"LAST_UPDATED={current_time}\n")
            f.write(f"CHANGELOG={phase_title}\n")
            output_delimiter = f"ghadelimiter_{uuid.uuid4().hex}"
            f.write(f"COMMIT_BODY<<{output_delimiter}\n")
            f.write(f"{commit_body}\n")
            f.write(f"{output_delimiter}\n")


def main() -> None:
    """Execute the blueprint update CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        nargs="?",
        default="auto",
        help="Simulation mode: auto, 1-4, or a manual phase alias.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="blueprints/motion_light_blueprint.yaml",
        help="Blueprint YAML file to update.",
    )
    args = parser.parse_args()
    update_blueprint(args.file, args.mode)


if __name__ == "__main__":
    main()
