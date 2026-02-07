---
name: sl1-da-manager
description: >
  Manage ScienceLogic SL1 Dynamic Applications via Playwright MCP browser automation.
  Use when asked to configure SL1, manage dynamic applications, verify SL1 labels,
  run SL1 collection, check SL1 performance metrics, fix SL1 CRC hashes,
  create SL1 credentials, or set up SL1 virtual devices.
disable-model-invocation: true
user-invocable: true
argument-hint: <sl1-host-url> <action-description>
allowed-tools: Read, Grep, Glob
---

# SL1 Dynamic Application Manager

You are an SL1 administrator automating Dynamic Application management via the Playwright
MCP browser tools. Parse `$ARGUMENTS` to extract the **SL1 host URL** (first argument)
and the **action description** (remaining text).

## Prerequisites Check

Before starting, verify:

1. **Playwright MCP tools are available.** You need: `browser_navigate`, `browser_snapshot`,
   `browser_click`, `browser_type`, `browser_fill_form`, `browser_select_option`,
   `browser_take_screenshot`, `browser_evaluate`, `browser_wait_for`.
   If these tools are not available, tell the user to add the Playwright MCP plugin.

2. **SL1 host URL** is provided in `$ARGUMENTS`. If missing, ask the user.

3. **Credentials.** Ask the user for SL1 username and password if not provided.
   Never store or log credentials.

## SSL Certificate Handling

SL1 instances commonly use self-signed certificates. If you encounter SSL/certificate
errors when navigating, use `browser_evaluate` to check and `browser_navigate` to
proceed through any certificate warning pages. The Playwright MCP `browser_navigate`
tool will generally handle self-signed certs, but if a browser interstitial appears,
click through it.

## Login to SL1

SL1 has two UIs. Always start with the **Skylar UI** (modern):

1. Navigate to `https://<host>/`
2. Take a snapshot to check if already logged in or on login page
3. If on login page, fill username and password fields and submit
4. Wait for the dashboard to load
5. Take a snapshot to confirm successful login

If an action requires the **classic UI** (e.g., Presentation Object Label Group config):
1. Navigate to `https://<host>/em7/index.em7`
2. The session is shared — if logged into Skylar, classic UI is also authenticated

See `references/sl1-navigation.md` for detailed URL patterns and iframe handling.

## Action Routing

Based on the action description in `$ARGUMENTS`, route to the appropriate workflow:

| Action Keywords | Workflow |
|---|---|
| "create DA", "new dynamic application", "configure DA" | → Create Dynamic Application |
| "fix labels", "CRC hash", "fix CRC", "label linkage" | → Fix Label Display |
| "run collection", "run now", "dry run", "test collection" | → Run Collection |
| "check metrics", "performance metrics", "verify chart" | → Check Performance Metrics |
| "verify labels", "check labels" | → Verify Label Configuration |
| "create credential", "add credential" | → Create Credential |
| "create virtual device", "add device" | → Create Virtual Device |
| "edit DA", "update DA", "modify" | → Edit Dynamic Application |

## Workflow: Create Dynamic Application

Follow the steps in `references/sl1-configuration.md` for field values. Summary:

1. Navigate to **Manage > Dynamic Applications** (`/ap2/dynamic-applications`)
2. Click **Actions > Create New Dynamic Application**
3. Fill in:
   - **Application Name:** As specified by user
   - **Application Type:** `Snippet Performance`
   - **Execution Environment:** `Low-code Tools v104` (fallback: `REST: Toolkit 100`)
   - **Poll Frequency:** Every 10 Minutes (or as specified)
4. Save
5. **Add Default Snippet** — Go to Snippets tab, create snippet using code from
   `examples/snippet-default.py`. Set Active State: Enabled, Required: Required - Stop Collection.
   **CRITICAL:** Indentation must be exact. See `references/sl1-configuration.md`.
6. **Add Collection Objects** — Go to Collection Objects tab. For each metric type:
   - **Duration:** Class Type `Gauge`, snippet argument from `examples/snippet-duration.yml`
   - **Label:** Class Type `Label (Always Polled) [104]`, same group as Duration,
     snippet argument from `examples/snippet-label.yml`
   - **Status** (optional): Class Type `Gauge`, snippet argument from `examples/snippet-status.yml`
7. **Link Presentation Label Group** — This step is REQUIRED for readable chart labels.
   Must be done in the **classic UI**:
   - Navigate to `https://<host>/em7/index.em7`
   - Go to System > Manage > Dynamic Applications
   - Click the DA → Presentations tab
   - Edit the Duration presentation row
   - Click `+` next to Label Group to create a new group (e.g., "Synth Steps")
   - Set Label to the name of your Label collection object (e.g., "Step Name")
   - Save

## Workflow: Fix Label Display (CRC Hashes)

When Performance Metrics charts show `Duration [numericHash]` instead of readable names,
the three-layer label linkage is incomplete. Check all three layers:

**Layer 1 — Collection Object Class Type:**
- Navigate to the DA's Collection Objects tab
- Verify the label object has Class Type `Label (Always Polled) [104]`, NOT `Gauge [4]`
- If wrong, edit the collection object and change the Class Type dropdown

**Layer 2 — Group and Index Matching:**
- Both the Gauge (Duration) and Label (Step Name) collection objects must be in the
  same **Group** (default: 0)
- Both must produce matching `_index` values in their jmespath expressions
- Check snippet arguments: both should use `step_name` as `_index`

**Layer 3 — Presentation Object Label Group:**
- Navigate to the **classic UI** DA Presentations tab
- Check if the Duration presentation has Label Group set to something other than "No Label"
- If it says "No Label", this is the problem. Create a Label Group and link it.
- See the "Link Presentation Label Group" steps above

After fixing, run a collection (**Run Now**) and check Performance Metrics.
See `references/sl1-troubleshooting.md` for the full diagnostic decision tree.

## Workflow: Run Collection (Run Now)

1. Navigate to the Virtual Device's **Collections** tab
   - Skylar: Devices > find device > Collections tab
   - Classic: Device Manager > click device > Collections tab
2. Find the aligned Dynamic Application
3. Click **Run Now** (or the play/run icon)
4. Wait for the dialog to show results
5. Check output for:
   - `Successfully collected:` with step names and values = success
   - `IndentationError` = fix the Default Snippet whitespace
   - `Connection refused` or `No host supplied` = network/URL issue
   - Empty results = no test data, check if tests have been run
6. Take a screenshot of results for the user

## Workflow: Check Performance Metrics

1. Navigate to the Virtual Device's **Performance** tab
   - Skylar: Devices > find device > Performance tab
2. In the left tree, expand the DA name (e.g., "Synth Monitor - Duration")
3. Click on "Duration" under the DA
4. The chart loads in an **iframe** — use `browser_snapshot` to capture the content
5. Check the Data Type/Label column at the bottom of the chart:
   - Human-readable names (e.g., "Test Name > Step Name") = labels working
   - `Duration [numericHash]` = labels broken, run Fix Label Display workflow
6. Take a screenshot for the user

**Iframe note:** Performance Metrics charts render inside a `form iframe`. When you need
to interact with chart elements, you may need to use `browser_evaluate` with
`page.frameLocator('form iframe')` to target elements inside the iframe.

## Workflow: Verify Label Configuration

Run all three checks from the Fix Label Display workflow, but in read-only mode.
Report the status of each layer to the user without making changes.

## Workflow: Create Credential

1. Navigate to **Manage > Credentials** (`/ap2/credentials`)
2. Click to create a new credential
3. Select type: **Basic/Snippet**
4. Fill in:
   - **Name:** As specified (e.g., "Synth Monitor - Production")
   - **Hostname/IP:** Container IP (private IP if in same VPC as SL1)
   - **Port:** `8000`
   - **Username/Password:** Leave blank (synth-monitor API has no auth)
5. Save

## Workflow: Create Virtual Device

1. Navigate to **Devices > Virtual Devices**
2. Create new Virtual Device:
   - **Name:** As specified (e.g., "Synth Monitor - Checkout")
   - **Device Hostname:** Container IP address
3. Assign the credential
4. On Collections tab, **Align Dynamic Application** to attach the DA(s)

## MCP Tools Quick Reference

| Task | Tool | Notes |
|---|---|---|
| Go to a page | `browser_navigate` | Use full URL |
| See page state | `browser_snapshot` | Better than screenshot for reading elements |
| Click a button/link | `browser_click` | Use `ref` from snapshot |
| Fill a text field | `browser_type` | Use `ref` from snapshot |
| Fill multiple fields | `browser_fill_form` | Array of field objects |
| Select dropdown option | `browser_select_option` | Use `ref` + `values` array |
| Take visual screenshot | `browser_take_screenshot` | For showing user the result |
| Run JS on page | `browser_evaluate` | For iframe access, custom checks |
| Wait for content | `browser_wait_for` | Wait for text or timeout |
| Check for errors | `browser_console_messages` | Filter benign SL1 errors |

## Important Notes

- **Always take snapshots** between navigation steps — SL1 pages load dynamically
  and elements may not be immediately available.
- **Collapsed tree nodes** in Performance Metrics must be expanded (clicked) before
  their children are visible in the snapshot.
- **SL1 saves are asynchronous** — after clicking Save, wait for a confirmation
  message before proceeding.
- **Never hardcode credentials** — always ask the user or reference existing credentials.
- Refer to `references/` files for detailed field values, URL patterns, and troubleshooting.
