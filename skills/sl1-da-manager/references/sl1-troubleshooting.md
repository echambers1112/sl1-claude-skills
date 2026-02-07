# SL1 Troubleshooting Reference

## Diagnostic Decision Tree

```
Performance Metrics shows "Duration [CRC_hash]" labels
│
├─ Check Layer 1: Collection Object Class Type
│  └─ Is the label object Class Type [104] Label (Always Polled)?
│     ├─ NO → Change from Gauge [4] to Label [104], save, Run Now
│     └─ YES → Continue to Layer 2
│
├─ Check Layer 2: Group and Index Matching
│  └─ Are Label and Gauge objects in the same Group?
│     ├─ NO → Set both to the same Group number (default: 0)
│     └─ YES → Do both jmespath expressions use the same _index field?
│        ├─ NO → Fix _index to use same field (step_name)
│        └─ YES → Continue to Layer 3
│
└─ Check Layer 3: Presentation Object Label Group
   └─ In classic UI: Does Duration presentation have a Label Group set?
      ├─ Shows "No Label" → Create Label Group, set Label field, save
      └─ Has a Label Group → Verify Label field points to correct object
         └─ Run Now and check chart again
```

## Common Errors and Fixes

### IndentationError in Default Snippet

**Symptom:** Run Now shows `IndentationError: unexpected indent` or similar Python error.

**Cause:** Whitespace corruption from copy-paste. SL1's web editor can insert invisible
characters or convert spaces to tabs.

**Fix:**
1. Navigate to DA → Snippets tab
2. Click to edit the Default Snippet
3. **Clear the entire Snippet Code field** (select all, delete)
4. Retype the code manually — do NOT paste. Type each line character by character.
5. Ensure lines 1-2 are flush left, all `with` block lines are 4-space indented
6. Save and Run Now to test

**Prevention:** When pasting the Default Snippet code, immediately Run Now to verify
before configuring collection objects.

### "No host supplied" or "Invalid URL"

**Symptom:** Run Now shows URL-related error.

**Cause:** `${silo_ip}` substitution variable didn't resolve.

**Fix:**
1. Check the Run Now output for "Final Execution Plan" — it shows the resolved URL
2. If the URL has a blank or malformed host, the variable didn't resolve
3. Edit the Collection Object's Snippet Argument
4. Replace `${silo_ip}` with the actual container IP address
5. Replace `${silo_comp_name}` with the actual group name
6. Save and Run Now

### Connection Refused

**Symptom:** Run Now shows `Connection refused` or timeout error.

**Cause:** Network connectivity issue between SL1 collector and container.

**Diagnosis:**
1. Verify container is running: `docker compose ps`
2. Check container logs: `docker compose logs monitor`
3. Test connectivity from SL1's perspective (if you have SSH access):
   `curl http://<container-ip>:8000/api/health`
4. Check security group / firewall rules — port 8000 must be open from SL1 collector

### Empty Steps Array

**Symptom:** Run Now succeeds but no collection objects appear, or the API returns
`"steps": []`.

**Cause:** No test data exists in the synth-monitor database.

**Fix:**
1. Check if tests are defined: `curl http://<ip>:8000/api/tests`
2. If no tests, run `npm run seed` in the container
3. Check if tests have been executed: `curl http://<ip>:8000/api/results/latest?group=<group>`
4. If no results, run tests manually: `npx playwright test`
5. Verify the group name matches what's in the test definitions

### Performance Counter vs Gauge Symptoms

**Symptom:** Chart shows "could not derive rate for counter" warnings, or graph values
are wildly incorrect (negative, near-zero, or nonsensical).

**Cause:** Collection Object Class Type is set to `Performance Counter` instead of `Gauge`.

**Explanation:** Performance Counter is for cumulative counters (like bytes transferred)
where SL1 calculates the rate of change between polls. Duration and status are
point-in-time values — SL1 tries to calculate `(current - previous) / time_delta`
which produces garbage for non-cumulative data.

**Fix:**
1. Navigate to DA → Collection Objects tab
2. Edit the offending collection object
3. Change Class Type from `Performance Counter` to `Gauge`
4. Save
5. **Note:** Historical data collected under the wrong class type will remain incorrect.
   New data will be correct after the next poll cycle.

### Stale Data / Old Millisecond Values

**Symptom:** Chart Y-axis shows values like 60,000 alongside values like 5.28.

**Cause:** The API was previously returning `duration_ms` (milliseconds) and was updated
to return `duration_s` (seconds). Old data in SL1's database still has the millisecond
values.

**Fix:** No action needed — the old data will age out per SL1's retention policy.
The chart will normalize once all old ms-scale data points expire. You can also
manually delete the old presentation data via the Series Selection dialog if needed.

### Labels Working in Classic UI But Not Skylar

**Symptom:** Classic UI Performance tab shows correct labels, Skylar Performance tab
still shows CRC hashes.

**Cause:** Skylar caches presentation data separately. The Label Group configuration
change may not be reflected immediately.

**Fix:** Force a fresh collection via Run Now. If still showing CRC hashes in Skylar,
navigate away from the device and back, or try a different browser/incognito window.

### Run Now Succeeds But No Chart Data

**Symptom:** Run Now shows successful collection with values, but Performance Metrics
chart is empty.

**Cause:** SL1 needs at least 2 data points to draw a chart line. With a single Run Now,
there's only one data point.

**Fix:** Run Now a second time (wait a few seconds between runs), or wait for the next
scheduled poll cycle.

## Verification Checklist

After configuring a DA, verify all components:

- [ ] Default Snippet exists and is Enabled + Required
- [ ] Default Snippet code has correct indentation (Run Now to test)
- [ ] Duration Collection Object: Class Type = Gauge, correct snippet argument
- [ ] Label Collection Object: Class Type = Label (Always Polled) [104]
- [ ] Label and Duration in same Group with matching `_index` (step_name)
- [ ] Presentation Object: Label Group created and linked (classic UI)
- [ ] Credential created with correct IP and port
- [ ] Virtual Device created with credential assigned
- [ ] DA aligned to Virtual Device
- [ ] Run Now produces expected collection objects with values
- [ ] Performance Metrics chart shows human-readable labels
