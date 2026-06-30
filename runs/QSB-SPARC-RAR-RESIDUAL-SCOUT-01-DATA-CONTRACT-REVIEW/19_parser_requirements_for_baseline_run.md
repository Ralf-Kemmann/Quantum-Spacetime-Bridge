# Parser Requirements for Baseline Run

The next baseline run should:

- parse MRT byte-by-byte label sections
- preserve raw files unchanged
- read `RAR.mrt` direct `gbar`/`gobs` columns for baseline reproduction where possible
- use `MassModels_Lelli2016c.mrt` only under an explicit derivation contract
- report parser row counts and label maps before any fit
- stop if checksums differ from this review
