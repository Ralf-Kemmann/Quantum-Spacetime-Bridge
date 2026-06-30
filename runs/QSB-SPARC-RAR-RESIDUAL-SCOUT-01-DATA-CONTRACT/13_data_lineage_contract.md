# Data Lineage Contract

Local input directory:

`runs/QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT/input`

Lineage requirements:

- every registered input file must have SHA256 recorded
- original downloaded/registered files must remain unmodified
- documentation/README/citation files must be stored with data files
- normalized or derived files must be created only in later run output locations
- no residual analysis before data contract is frozen
- source references may be carried from repo artifacts, but external retrieval is not performed in this run
