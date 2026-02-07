# SL1 Navigation Reference

## Dual UI Architecture

SL1 has two concurrent web interfaces sharing the same session:

| UI | Base Path | Use For |
|---|---|---|
| **Skylar** (modern) | `/ap2/` | Most admin tasks, DA creation, device management |
| **Classic** | `/em7/index.em7` | Presentation Object Label config, some legacy settings |

Both UIs authenticate against the same session. Logging into Skylar also authenticates
the classic UI, and vice versa.

## URL Patterns

### Skylar UI (`/ap2/`)

| Page | URL Pattern |
|---|---|
| Dashboard | `https://<host>/` or `https://<host>/ap2/` |
| Dynamic Applications | `https://<host>/ap2/dynamic-applications` |
| DA Detail | `https://<host>/ap2/dynamic-application/<app_id>` |
| Credentials | `https://<host>/ap2/credentials` |
| Devices | `https://<host>/ap2/devices` |
| Device Detail | `https://<host>/ap2/device/<device_id>` |
| Virtual Devices | `https://<host>/ap2/virtual-devices` |

### Classic UI (`/em7/`)

| Page | URL Pattern |
|---|---|
| Main | `https://<host>/em7/index.em7` |
| DA List | `https://<host>/em7/index.em7?exec=admin_dynamic_app` |
| DA Detail | `https://<host>/em7/index.em7?exec=admin_dynamic_app&function=edit&app_id=<id>` |
| DA Snippets | `https://<host>/em7/index.em7?exec=admin_dynamic_app_snippet&app_id=<id>` |
| DA Collection Objects | `https://<host>/em7/index.em7?exec=admin_dynamic_app_object&app_id=<id>` |
| DA Presentations | `https://<host>/em7/index.em7?exec=admin_dynamic_app_present&app_id=<id>` |
| Presentation Edit | `...&function=edit&presentation_id=<pres_id>&app_id=<app_id>` |
| Device Manager | `https://<host>/em7/index.em7?exec=device_summary` |

## Login Flow

### Skylar UI Login

1. Navigate to `https://<host>/`
2. Snapshot — look for username/password fields
3. Fill username field, fill password field
4. Click the login/sign-in button
5. Wait for dashboard to load (look for navigation elements)
6. Snapshot to confirm login success

### Classic UI Login

Usually not needed if already logged into Skylar. If required:
1. Navigate to `https://<host>/em7/index.em7`
2. Fill username and password fields
3. Submit the form

## Iframe Handling

**Performance Metrics charts** render inside an iframe:

```
page
  └── form iframe
        └── chart content (Data Type/Label table, graph)
```

When interacting with chart elements:
- `browser_snapshot` captures the main page — iframe content may appear as a nested section
- To click elements inside the iframe, use `browser_evaluate`:
  ```javascript
  async (page) => {
    const frame = page.frameLocator('form iframe');
    await frame.locator('text=Duration').click();
  }
  ```
- If snapshot shows iframe content inline, you can use regular `browser_click` with the ref

## Tree Node Navigation (Performance Metrics)

The left-side tree in Performance Metrics has collapsible nodes:

1. **Snapshot** the page to see the tree structure
2. **Collapsed nodes** show with an expand icon — click to expand
3. **After expanding**, snapshot again to see child nodes
4. **Click the leaf node** (e.g., "Duration") to load that chart

Pattern:
```
▶ Synth Monitor - Duration    ← Click to expand
  └── Duration                ← Now visible, click to load chart
  └── * Step Name             ← Label object (asterisk prefix)
```

The asterisk (`*`) prefix on "Step Name" indicates it's a Label class type object.

## Console Errors (Safe to Ignore)

SL1 generates several benign console errors during normal operation:

- **`Uncaught TypeError: Cannot read properties of null`** — Common in SL1's own JS,
  does not affect functionality
- **`404 Not Found` for static assets** — Missing icons or fonts, cosmetic only
- **`Mixed content` warnings** — When SL1 loads HTTP resources from an HTTPS page
- **`ResizeObserver loop`** — Browser layout engine warning, harmless
- **jQuery deprecation warnings** — SL1 uses legacy jQuery patterns

Do NOT report these to the user unless they ask about console errors specifically.

## Navigation Tips

- **Wait after navigation** — SL1 pages use AJAX loading. After `browser_navigate`,
  use `browser_wait_for` with expected text or a brief timeout before taking a snapshot.
- **Dropdowns** — SL1 uses custom dropdowns that may require clicking to open, then
  clicking the option. Use `browser_snapshot` after opening to find option refs.
- **Save confirmation** — After clicking Save, look for confirmation text like
  "Object Saved" or a success banner in the next snapshot.
- **Tab navigation** — DA detail pages have tabs (Snippets, Collection Objects,
  Presentations). Click the tab header to switch; snapshot to verify the tab loaded.
