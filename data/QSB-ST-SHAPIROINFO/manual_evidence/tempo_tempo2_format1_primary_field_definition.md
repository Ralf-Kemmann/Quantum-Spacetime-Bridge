# TEMPO/TEMPO2 FORMAT 1 Primary Field Definition Evidence

## Identity

```text
evidence_id: TEMPO_TEMPO2_FORMAT1_PRIMARY_FIELD_DEFINITION
evidence_type: external_primary_documentation
evidence_status: supported
format_name: TEMPO/TEMPO2 FORMAT 1
```

## Documented Field Semantics

```text
field_position_1: observation_or_profile_identifier
field_position_2: observing_frequency
field_position_2_unit: MHz
field_position_3: TOA_or_site_arrival_time
field_position_3_unit: MJD
field_position_4: TOA_uncertainty
field_position_4_unit: microseconds
field_position_5: observatory_or_site_identifier
field_position_6_plus: optional_flags
```

## Applicability

```text
applies_to_file: J0740+6620.cfr+19.tim
applicability_condition: file contains FORMAT 1 header
format_header_confirmed: yes
maps_to_tim_token_003: no
```

## Scope Boundary

This evidence documents the official FORMAT 1 file layout.
It does not establish any mapping from the official TIM fields
to the previously unresolved internal database token tim_token_003.

## Time-Basis Boundary

The documentation supports the file-level TOA field and its MJD unit.
It does not by itself validate the complete model-consistent clock
correction, observatory-time, barycentric-time, or TDB processing chain.

## Provenance

### Source A1

```text
source_title: TEMPO reference manual TOA lines section
source_organization: TEMPO project / SourceForge
source_url: https://tempo.sourceforge.net/ref_man_sections/toa.txt
retrieval_timestamp_utc: 2026-06-05T22:16:20Z
local_path: data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo_reference_toa_format.txt
file_size_bytes: 2909
sha256: 67fc99940b76236460c7eb2e13e09edc7db8a095386b3ac17ff1e5bdca168fb4
mime_or_file_type: ASCII text
relevant_section_or_search_phrase: Tempo2 Format; FORMAT 1; field 3 TOA; TOAs are reported as MJD
retrieval_status: downloaded_via_curl_exit_0_and_local_validation_passed
notes: Supports whitespace-separated FORMAT 1 field order, field 3 as TOA, frequency in MHz, uncertainty in microseconds, observatory code, optional flags, and TOA reporting as MJD. Does not validate full model time-scale processing.
```

### Source A2

```text
source_title: TEMPO2 examples
source_organization: Jodrell Bank Centre for Astrophysics / University of Manchester
source_url: https://www.jb.man.ac.uk/~pulsar/Resources/tempo2_examples_ver1.pdf
retrieval_timestamp_utc: 2026-06-05T22:16:20Z
local_path: data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo2_examples_ver1.pdf
file_size_bytes: 912265
sha256: 1e56bb859892f7baf1b8ea41e947734ccca31cd1f3c07e24b786d8252eff3798
mime_or_file_type: PDF document, version 1.5
relevant_section_or_search_phrase: Arrival time files; FORMAT 1; frequency; MJD; uncertainty
retrieval_status: downloaded_via_curl_exit_0_and_local_validation_passed
notes: Supports FORMAT 1 arrival-time-file order and documents frequency in MHz, arrival time in MJD, and uncertainty in microseconds. Does not validate full model time-scale processing.
```

### Source A3

```text
source_title: TEMPO2 user manual
source_organization: Jodrell Bank Centre for Astrophysics / University of Manchester
source_url: https://www.jb.man.ac.uk/research/pulsar/Resources/tempo2_manual.pdf
retrieval_timestamp_utc: 2026-06-05T22:16:20Z
local_path: data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo2_manual.pdf
file_size_bytes: 601430
sha256: 76ef6400c2de297e3b2c5ebac1a4a94edfda621cc1f24ac937d7e46d503affaa
mime_or_file_type: PDF document, version 1.3, 35 pages
relevant_section_or_search_phrase: Observation files; FORMAT 1; file freq sat satErr siteID <flags>; site-arrival-times
retrieval_status: downloaded_via_curl_exit_0_and_local_validation_passed
notes: Supports the TEMPO2 observation-file FORMAT 1 field order and describes TIM entries as site-arrival-times. Used as supplementary field-order evidence only; full time-scale validation remains outside this update.
```

## Evidence Threshold

```text
field_order_supported_by_at_least_one_official_source: yes
toa_position_supported_by_at_least_one_official_source: yes
toa_mjd_unit_supported_by_at_least_one_official_source: yes
uncertainty_microseconds_supported_by_at_least_one_official_source: yes
full_model_time_scale_supported: no
```
