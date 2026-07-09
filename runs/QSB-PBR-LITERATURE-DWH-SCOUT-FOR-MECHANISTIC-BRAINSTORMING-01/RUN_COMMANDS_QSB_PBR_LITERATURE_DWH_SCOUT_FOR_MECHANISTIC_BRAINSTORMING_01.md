# Run Commands

Run package:

`runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/`

Commands recorded for this read-only DWH literature scout:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
git status --short --untracked-files=all
git log --oneline -12
psql -d qsb_research_dwh -c "\dt"
psql -d qsb_research_dwh -c "\dn"
psql -d qsb_research_dwh -A -F ',' -c "SELECT table_schema, table_name FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema NOT IN ('pg_catalog','information_schema') ORDER BY table_schema, table_name;"
psql -d qsb_research_dwh -A -F ',' -c "SELECT table_schema, table_name, column_name, data_type FROM information_schema.columns WHERE lower(column_name) SIMILAR TO '%(title|author|year|doi|arxiv|bibtex|source|literature|paper|url|abstract|topic|keyword|claim|note|lineage)%' ORDER BY table_schema, table_name, ordinal_position;"
psql -d qsb_research_dwh -c "\d qsb_literature.reference_source"
psql -d qsb_research_dwh -c "\d qsb_literature.reference_claim_map"
psql -d qsb_research_dwh -c "\d qsb_literature.litnote_run"
psql -d qsb_research_dwh -A -F $'\t' -c "SELECT bib_key,run_id,work_package,entry_type,title,authors,year,COALESCE(journal,booktitle,'') AS venue,doi,arxiv_id,url,note,keywords,source_file,source_sha256,claim_status,physical_claim_release FROM qsb_literature.reference_source ORDER BY bib_key;"
psql -d qsb_research_dwh -A -F $'\t' -c "SELECT claim_map_id,run_id,bib_key,pillar_id,supports,does_not_support,qsb_connection,allowed_claim,forbidden_claim,review_status FROM qsb_literature.reference_claim_map ORDER BY bib_key,claim_map_id;"
psql -d qsb_research_dwh -A -F $'\t' -c "SELECT run_id,work_package,artifact_kind,source_bib_file,source_sha256,source_entry_count,claim_map_count,claim_boundary,physical_claim_status,lineage_note FROM qsb_literature.litnote_run ORDER BY run_id;"
mkdir -p runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/data runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/docs runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/validation runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/sql
psql -d qsb_research_dwh -f runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/sql/001_schema_discovery.sql
psql -d qsb_research_dwh -f runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/sql/002_literature_extraction.sql
psql -d qsb_research_dwh -f runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/sql/003_mechanistic_classification_notes.sql
sed -n '1,12p' runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/data/dwh_literature_inventory.csv
sed -n '1,12p' runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/data/dwh_literature_mechanism_axes.csv
sed -n '1,16p' runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/validation/validation_results.csv
git diff --check
git status --short --untracked-files=all
git status --short --ignored=matching runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01
```

No DWH write, import, candidate upgrade, mechanism test, or nullmodel command was run.
