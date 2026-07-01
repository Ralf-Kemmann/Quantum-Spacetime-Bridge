#!/usr/bin/env bash
set -eu

cat <<'NOTE'
This script does not install a system service.

To prepare a user service manually:

1. Copy scripts/qsb_metadata_server/qsb-metadata-server.service.example to:
   ~/.config/systemd/user/qsb-metadata-server.service
2. Review ExecStart and WorkingDirectory paths.
3. Run, if desired:
   systemctl --user daemon-reload
   systemctl --user enable --now qsb-metadata-server.service

The metadata server is read-only and uses psql against qsb_research_dwh.
NOTE
