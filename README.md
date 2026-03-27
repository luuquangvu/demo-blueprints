# Demo Blueprints for Blueprints Updater

This repository contains sample blueprints used for testing and demonstrating the [Blueprints Updater](https://github.com/luuquangvu/blueprints-updater) integration for Home Assistant.

---

## Blueprints

### Motion-Activated Light/Switch (Daily Update)

- **File**: `blueprints/motion_light_blueprint.yaml`
- **Description**: A simple blueprint that turns on a light or switch when motion is detected and turns it off when motion stops. This file is updated automatically every day via GitHub Actions to simulate a new version release.

**Quick Import:**
[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fluuquangvu%2Fdemo-blueprints%2Fblob%2Fmain%2Fblueprints%2Fmotion_light_blueprint.yaml)

**Manual Import:**

1. Copy the **Blueprint URL** `https://github.com/luuquangvu/demo-blueprints/blob/main/blueprints/motion_light_blueprint.yaml`.
2. In Home Assistant, go to **Settings** > **Automations & Scenes** > **Blueprints**.
3. Click **Import Blueprint** (bottom right).
4. Paste the URL and click **Preview**.
5. Click **Import Blueprint**.

## Automation

This repository uses GitHub Actions to automatically update the version and timestamp of the test blueprint daily. This allows users of the [Blueprints Updater](https://github.com/luuquangvu/blueprints-updater) integration to see the update process in action.
