# QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01 — Summary

**Work package:** QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01  
**Created:** 2026-07-03  
**Status:** scale_mapping_candidate  
**Physical claim release:** blocked_no_physics_claim  
**Review:** requires_dimensional_and_physical_review

## Content

- 1 Markdown theory note
- 2 mapping definitions
- 14 variable registry entries
- 3 special cases
- 4 claim boundaries
- 7 dimensional checks
- PostgreSQL import SQL
- PostgreSQL validation SQL
- Metadata integration SQL
- Metadata validation SQL

## Core mappings

```text
beta_B = r_s / lambda_C = 2 * G * m^2 / (hbar * c)
```

```text
Xi_CS = c_comp^2 / c_schwarz^2
      = hbar^2 * r_s / (2 * G * m_schwarz * m_comp^2 * lambda_C^2)
```

## Claim boundary

The mappings provide algebraic scale gates only. They do not prove a Planck-Bridge-Resonator and do not redefine the physical speed of light.
