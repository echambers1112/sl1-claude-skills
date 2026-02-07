# sl1-claude-skills

Claude Code plugin for managing ScienceLogic SL1 Dynamic Applications via Playwright MCP browser automation.

## What This Does

This plugin gives Claude Code the institutional knowledge to navigate SL1's dual web interfaces (Skylar + Classic), configure Dynamic Applications with the Snippet Framework, diagnose CRC hash label issues, and verify Performance Metrics charts — all via Playwright MCP browser tools.

### Included Skills

| Skill | Description |
|---|---|
| `sl1-da-manager` | Create, configure, troubleshoot, and verify SL1 Dynamic Applications |

### Capabilities

- Create Snippet Performance Dynamic Applications with correct field values
- Configure Collection Objects (Duration/Gauge, Label/104, Status/Gauge)
- Fix the three-layer label linkage that causes CRC hash labels on charts
- Run dry-run collections and interpret results
- Navigate Performance Metrics charts (including iframe handling)
- Create Credentials and Virtual Devices
- Diagnose IndentationError, connection issues, empty data, and more

## Prerequisites

1. **Claude Code** with plugin support
2. **Playwright MCP plugin** installed and configured — this skill uses browser automation tools (`browser_navigate`, `browser_snapshot`, `browser_click`, etc.)
3. **Network access** to your SL1 instance from where Claude Code is running
4. **SL1 credentials** (username/password) — the skill will ask for these at runtime

## Installation

```bash
# Add the marketplace (from GitHub)
claude plugin marketplace add echambers1112/sl1-claude-skills

# Or add from a local clone
claude plugin marketplace add /path/to/sl1-claude-skills

# Install the plugin
claude plugin install sl1-claude-skills@sl1-claude-skills
```

## Usage

Invoke the skill with the SL1 host URL and an action description:

```
/sl1-claude-skills:sl1-da-manager https://your-sl1-host.com configure new DA for group checkout
```

### Example Commands

```bash
# Create a new Dynamic Application
/sl1-claude-skills:sl1-da-manager https://52.11.87.56 create DA "Synth Monitor - Checkout" for group checkout

# Fix CRC hash labels on charts
/sl1-claude-skills:sl1-da-manager https://52.11.87.56 fix labels for device 8

# Run a dry-run collection
/sl1-claude-skills:sl1-da-manager https://52.11.87.56 run collection on virtual device "Synth Monitor - Production"

# Check Performance Metrics
/sl1-claude-skills:sl1-da-manager https://52.11.87.56 check performance metrics for device 8

# Verify label configuration
/sl1-claude-skills:sl1-da-manager https://52.11.87.56 verify labels for device 8

# Create a credential
/sl1-claude-skills:sl1-da-manager https://52.11.87.56 create credential for 172.31.11.45:8000
```

## Repo Structure

```
sl1-claude-skills/
├── .claude-plugin/
│   ├── plugin.json                 # Plugin manifest
│   └── marketplace.json            # Marketplace manifest (for installation)
├── plugins/sl1-claude-skills/
│   ├── .claude-plugin/
│   │   └── plugin.json             # Plugin entry point
│   └── skills/sl1-da-manager/
│       ├── SKILL.md                # Core workflow and action routing
│       ├── references/
│       │   ├── sl1-navigation.md   # Dual UI architecture, URLs, iframe handling
│       │   ├── sl1-configuration.md # DA fields, snippet code, collection objects, labels
│       │   └── sl1-troubleshooting.md # Diagnostic decision tree, common errors
│       └── examples/
│           ├── snippet-default.py  # Default Snippet Python boilerplate
│           ├── snippet-duration.yml # Duration collection object (Gauge, seconds)
│           ├── snippet-label.yml   # Label collection object (Class Type 104)
│           └── snippet-status.yml  # Status collection object (Gauge, pass/fail)
├── README.md
└── LICENSE
```

## Key Concepts

### Three-Layer Label Linkage

SL1 charts show `Duration [CRC_hash]` labels unless all three layers are configured:

1. **Collection Object Class Type** — Label object must be `Label (Always Polled) [104]`
2. **Group + Index Matching** — Label and Gauge objects in same group with matching `_index`
3. **Presentation Object Label Group** — Must be configured in the classic UI

This is the most common issue when setting up SL1 integrations. The skill knows how to diagnose and fix all three layers.

### Synth Monitor API Contract

The skill is designed to work with the [synth-monitor](https://github.com/echambers/scilo-synth-monitor) API endpoint:

```
GET /api/results/latest?group={group}
```

Response shape (consumed by SL1 jmespath):
```json
{
  "container_id": "abc123",
  "group": "device-health",
  "polled_at": "2026-02-07T12:00:00.000Z",
  "steps": [
    {
      "step_name": "checkout_transaction__login",
      "display_name": "Checkout Transaction > Login",
      "status": 1,
      "duration_s": 2.34,
      "error": null,
      "last_run": "2026-02-07T11:55:00.000Z"
    }
  ]
}
```

## License

MIT
