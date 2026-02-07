# SL1 Default Snippet — Snippet Framework Bootstrap
#
# This Python code is required in every Snippet Performance Dynamic Application.
# It bootstraps the SL1 Snippet Framework which processes the low_code YAML
# in each Collection Object's Snippet Argument.
#
# IMPORTANT: Indentation must be exact.
#   - Lines 1-2 (from/with) must be flush left (no leading spaces)
#   - All lines inside the `with` block must be indented exactly 4 spaces
#   - No tabs — spaces only
#   - If pasting into SL1 causes IndentationError, clear the field and retype manually
#
# Configuration:
#   Snippet Name:  Default Snippet
#   Active State:  Enabled
#   Required:      Required - Stop Collection

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
