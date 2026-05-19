# Syosset Fire Department — Home Assistant Integration

A custom component that scrapes [syossetfd.org](https://www.syossetfd.org/) and exposes the most recent fire alarm as a Home Assistant sensor.

## What it does

Polls the Syosset FD website on a configurable interval and creates one sensor:

| | |
|---|---|
| **State** | Alarm number of the newest alarm (monotonically increasing) |
| **Attributes** | `alarm`, `date`, `time`, `location`, `type` |

Because the alarm number only ever goes up, a state-change trigger in an automation reliably means a new alarm was dispatched.

## Installation

1. Copy the `custom_components/syosset_fd/` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for **Syosset Fire Department**.
4. Enter the desired poll interval (default: 5 minutes).

### Requirements

`beautifulsoup4>=4.9.0` is listed in `manifest.json` and will be installed automatically by Home Assistant.

## Configuration

| Option | Default | Range | Description |
|---|---|---|---|
| Update interval | 5 min | 1–1440 min | How often to poll the website |

## Example automation

```yaml
automation:
  - alias: "New Syosset FD alarm"
    trigger:
      - platform: state
        entity_id: sensor.syosset_fire_department_latest_alarm
    action:
      - service: notify.mobile_app
        data:
          title: "Syosset FD Alarm #{{ trigger.to_state.state }}"
          message: >
            {{ trigger.to_state.attributes.type }}
            at {{ trigger.to_state.attributes.location }}
            ({{ trigger.to_state.attributes.date }} {{ trigger.to_state.attributes.time }})
```

## How it works

The main site is a legacy frameset. Alarm data lives in `control/losapiframe.php`, an iframe that requires a `Referer` header from the parent page to serve content. The integration fetches that iframe directly with the correct headers and parses the HTML table with BeautifulSoup.
