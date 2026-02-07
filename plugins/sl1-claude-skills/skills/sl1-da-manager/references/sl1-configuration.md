# SL1 Configuration Reference

## Dynamic Application Fields

| Field | Value | Notes |
|---|---|---|
| Application Type | `Snippet Performance` | NOT "API" — that type doesn't exist in SL1 |
| Execution Environment | `Low-code Tools v104` | Built-in. Fallback: `REST: Toolkit 100` (from REST Toolkit PowerPack) |
| Poll Frequency | Every 10 Minutes | Match to test schedule; can be adjusted |

## Default Snippet Code

Every Snippet Performance DA requires a Default Snippet. This Python code bootstraps
the SL1 Snippet Framework.

**File:** `examples/snippet-default.py`

```python
from silo.apps.errors import error_manager
with error_manager(self):
    # ---- User Editable ----
    # ---- End User Editable ----
    from silo.low_code import *
    from silo.apps.collection import create_collections, save_collections

    # ---- User Editable ----
    custom_substitution = {}
    # ---- End User Editable ----

    collections = create_collections(self)
    snippet_framework(collections, custom_substitution, snippet_id, app=self)
    save_collections(collections, self)
```

### Indentation Rules (CRITICAL)

- Lines 1-2 (`from` and `with`) must be **flush left** (column 0, no leading spaces)
- All lines inside the `with` block must be indented **exactly 4 spaces**
- **No tabs.** Python will throw `IndentationError` with mixed whitespace
- SL1's web editor can mangle whitespace on paste — if you get `IndentationError`,
  clear the entire field and retype manually character by character
- The `# ---- User Editable ----` comments are SL1 conventions, not functional

### Snippet Configuration Fields

| Field | Value |
|---|---|
| Snippet Name | `Default Snippet` |
| Active State | Enabled |
| Required | Required - Stop Collection |

## Collection Object Types

### Duration (Gauge)

Collects step execution time in seconds.

| Field | Value |
|---|---|
| Object Name | `Duration` |
| Class Type | `Gauge` [4] |
| Group | `0` (default) |
| Snippet | `Default Snippet` |

**Snippet Argument:** See `examples/snippet-duration.yml`

```yaml
low_code:
  version: 2
  steps:
    - http:
        method: get
        url: "http://{CONTAINER_IP}:8000/api/results/latest?group={GROUP}"
    - json
    - jmespath:
        value: "steps[].{_index: step_name, _value: duration_s}"
        index: true
```

### Label (Always Polled)

Provides human-readable display names for chart legends. **Must be in the same group
as the Gauge object with matching `_index` values.**

| Field | Value |
|---|---|
| Object Name | `Step Name` |
| Class Type | `Label (Always Polled)` [104] |
| Group | `0` (same as Duration) |
| Snippet | `Default Snippet` |

**Snippet Argument:** See `examples/snippet-label.yml`

```yaml
low_code:
  version: 2
  steps:
    - http:
        method: get
        url: "http://{CONTAINER_IP}:8000/api/results/latest?group={GROUP}"
    - json
    - jmespath:
        value: "steps[].{_index: step_name, _value: display_name}"
        index: true
```

### Status (Gauge)

Collects pass/fail status (1 = passed, 0 = failed).

| Field | Value |
|---|---|
| Object Name | `Status` |
| Class Type | `Gauge` [4] |
| Group | `0` (or separate group from Duration) |
| Snippet | `Default Snippet` |

**Snippet Argument:** See `examples/snippet-status.yml`

```yaml
low_code:
  version: 2
  steps:
    - http:
        method: get
        url: "http://{CONTAINER_IP}:8000/api/results/latest?group={GROUP}"
    - json
    - jmespath:
        value: "steps[].{_index: step_name, _value: status}"
        index: true
```

## Three-Layer Label Linkage

For Performance Metrics charts to show human-readable labels instead of
`Duration [CRC_hash]`, ALL three layers must be configured:

### Layer 1: Collection Object Class Type

The label collection object must have Class Type **`Label (Always Polled)` [104]**.

Common mistake: Setting it to `Gauge` [4] — SL1 treats it as another metric, not a label.

### Layer 2: Group and Index Matching

- The Label and Gauge collection objects must be in the **same Group** (both default to 0)
- Both jmespath expressions must produce the same `_index` values (`step_name`)
- The Label's `_value` is the display text (`display_name`)

### Layer 3: Presentation Object Label Group

**This step is done in the classic UI only.**

1. Navigate to `https://<host>/em7/index.em7`
2. Go to System > Manage > Dynamic Applications
3. Click the DA → **Presentations** tab
4. In the Presentation Object Registry, click the wrench/edit icon on the **Duration** row
5. Find the **Label Group** dropdown (shows "No Label" by default)
6. Click the `+` icon next to Label Group to create a new group
7. Enter a name (e.g., `Synth Steps`)
8. Set the **Label** dropdown to the name of your Label collection object (e.g., `Step Name`)
9. Save

**Missing any layer = CRC hash labels on charts.**

## SL1 Substitution Variables

| Variable | Resolves To | Reliability |
|---|---|---|
| `${silo_ip}` | Device hostname/IP from credential | Unreliable — may not resolve on Virtual Devices |
| `${silo_comp_name}` | Component name / device name | Unreliable — may not resolve |
| `${silo_dev_id}` | Device ID | Usually works |

**Recommendation:** Hardcode the container IP and group name in snippet arguments.
The substitution variables are designed for SNMP-style monitoring and don't always
work with Virtual Devices and the Snippet Framework. Test with **Run Now** first
if you want to try them.

## Credential Setup

| Field | Value |
|---|---|
| Type | Basic/Snippet |
| Name | `Synth Monitor - <environment>` |
| Hostname/IP | Container's private IP (if same VPC as SL1) |
| Port | `8000` |
| Username | (blank — no auth) |
| Password | (blank — no auth) |

## Virtual Device Setup

| Field | Value |
|---|---|
| Name | `Synth Monitor - <group name>` |
| Device Hostname | Container IP address |
| Credential | The credential created above |
| Aligned DAs | Duration DA + Status DA (optional) |

**Mapping:** Multiple Virtual Devices can point to the same container with different
`?group=` values in the snippet arguments. Each VD represents a test group.

## Threshold Configuration

### Duration Thresholds (values in seconds)

| Condition | Severity | Meaning |
|---|---|---|
| `value > 5` | Warning | Step taking > 5 seconds |
| `value > 10` | Critical | Step taking > 10 seconds |
| `value > 30` | Major | Step taking > 30 seconds |

### Status Thresholds

| Condition | Severity | Meaning |
|---|---|---|
| `value == 0` | Critical | Step failed |

### Availability

The HTTP step itself fails if the container is unreachable, triggering an SL1
availability alert on the Virtual Device automatically.
