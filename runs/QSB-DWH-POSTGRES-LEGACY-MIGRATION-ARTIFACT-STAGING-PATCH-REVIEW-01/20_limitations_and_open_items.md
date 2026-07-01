# Limitations And Open Items

1. CSV generic staging capped at 100000 rows.
2. Generic artifact staging is not equivalent to domain-semantic canonical loading.
3. Some domain overview views may require later semantic loaders.
4. Global search contains broad artifact text and may include noise/duplicates.
5. Oversized replay SQL files are local-only and represented by omission notes.
6. SQLite catalogs are inventoried/imported at catalog level; semantic meta_* import must be reviewed per catalog.
7. No physical interpretation may proceed before domain-specific review gates approve the relevant subset.
