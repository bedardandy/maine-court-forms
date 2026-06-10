#!/usr/bin/env python3
"""Synthesize a minimal ZapfDingbats TrueType — shim over the shared
``maine-forms-engine`` (``maine_forms_engine.accessibility.make_zapf_ttf``;
ships verbatim there as embed_widget_font's optional fallback).
"""
from maine_forms_engine.accessibility.make_zapf_ttf import (  # noqa: F401
    DEJAVU_CANDIDATES,
    ZAPF_TO_UNI,
    build,
    ensure,
)
