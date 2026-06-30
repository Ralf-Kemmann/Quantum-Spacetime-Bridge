# Parser Edge Cases

- MRT byte ranges were parsed from byte-by-byte sections.
- Whitespace fallback is available when fixed-width slicing produces empty fields.
- Direct `RAR.mrt` rows do not include galaxy/radius identifiers in the parsed labels.
- MassModels-derived final `g_bar` requires mass-to-light assumptions and is not finalized here.
- Negative gas velocity contributions are preserved through `Vgas * abs(Vgas)` only for preparatory component handling.
