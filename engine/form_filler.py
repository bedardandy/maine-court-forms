"""Form filler — shim over the shared ``maine-forms-engine``.

This repo was the extraction donor: the implementation moved verbatim into
``maine_forms_engine.fill.form_filler`` and the package defaults ARE this
repo's behavior. This module keeps the repo's ``engine.form_filler`` import
path and API stable:

- ``fill_form`` / ``fill_form_from_json`` return the output path (the donor
  contract; the package's ``return_report=True`` diagnostics dict is the
  tax-repo dialect and is not used here).
- every ``addendum_policy`` is accepted; ``"auto"`` fails at overflow time
  with the donor's ValueError because the addendum renderer lives in this
  repo's recipe layer (``engine/fill_and_audit.py``), not in the engine.
"""
from maine_forms_engine.fill.form_filler import (  # noqa: F401
    BODY_FONT,
    _group_widgets_by_name,
    _multi_widget_mode,
    _split_address_at_commas,
    _widget_capacity_chars,
    _wrap_across_widgets,
    fill_form,
    fill_form_from_json,
    generate_template,
    list_form_fields,
)
