# Demo Blueprints for Blueprints Updater

This repository contains sample blueprints used for testing and demonstrating the [Blueprints Updater](https://github.com/luuquangvu/blueprints-updater) integration for Home Assistant.

---

## Blueprints

### Motion-Activated Light/Switch (Frequent Updates)

- **File**: `blueprints/motion_light_blueprint.yaml`
- **Description**: A simple blueprint that turns on a light or switch when motion is detected and turns it off when motion stops. This file is updated frequently via GitHub Actions to simulate new releases.

**Quick Import:**
[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fluuquangvu%2Fdemo-blueprints%2Fblob%2Fmain%2Fblueprints%2Fmotion_light_blueprint.yaml)

**Manual Import:**

1. Copy the **Blueprint URL** `https://github.com/luuquangvu/demo-blueprints/blob/main/blueprints/motion_light_blueprint.yaml`.
2. In Home Assistant, go to **Settings** > **Automations & Scenes** > **Blueprints**.
3. Click **Import Blueprint** (bottom right).
4. Paste the URL and click **Preview**.
5. Click **Import Blueprint**.

## Unique Blueprints Collection

Ready to go beyond standard automations? Unlock the true potential of your smart home with my **exclusive collection of custom-built blueprints**.

[**luuquangvu/tutorials**](https://github.com/luuquangvu/tutorials)

These unique, AI-powered solutions are designed to push the boundaries of Home Assistant, featuring high-level integrations-from **Voice Assist intelligence** to **sophisticated smart logic** - that you won't find anywhere else. Transform your home into a truly proactive, intelligent companion today.

## Automation

This repository uses GitHub Actions to automatically update the unique `update_id` (UUID) and timestamp of the test blueprint frequently. This allows users of the [Blueprints Updater](https://github.com/luuquangvu/blueprints-updater) integration to see the update process in action.
