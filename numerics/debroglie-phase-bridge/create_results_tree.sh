#!/usr/bin/env bash
set -euo pipefail

# Create a project results directory tree for the current debroglie-phase-bridge workflow.
# Usage:
#   chmod +x create_results_tree.sh
#   ./create_results_tree.sh
# Optional:
#   ./create_results_tree.sh results
#   ./create_results_tree.sh /absolute/path/to/results

ROOT="${1:-results}"

echo "Creating results tree under: ${ROOT}"

mkdir -p \
  "${ROOT}/k0/smoke_test" \
  "${ROOT}/k0/t1_smoke_test" \
  "${ROOT}/n0/smoke_test_seed_12345" \
  "${ROOT}/n0/ensemble_smoke_test" \
  "${ROOT}/n0/ensemble_50" \
  "${ROOT}/n1a/alpha_0p5_smoke_test" \
  "${ROOT}/n1a/alpha_2p0_smoke_test" \
  "${ROOT}/n1a/alpha_0p5_t1_smoke_test" \
  "${ROOT}/n1a/alpha_2p0_t1_smoke_test" \
  "${ROOT}/n1a_scan/k0_t1" \
  "${ROOT}/n1a_scan/n1a_alpha_0p5_t1" \
  "${ROOT}/n1a_scan/n1a_alpha_2p0_t1" \
  "${ROOT}/n1a_scan/interval_map" \
  "${ROOT}/t1/k0_reference_theta_map" \
  "${ROOT}/t1/n0_theta_ensemble" \
  "${ROOT}/t1/k0_vs_n0_theta" \
  "${ROOT}/a1_probe/k0/abs" \
  "${ROOT}/a1_probe/k0/positive" \
  "${ROOT}/a1_probe/k0/negative" \
  "${ROOT}/a1_probe/n1a_alpha/abs" \
  "${ROOT}/a1_probe/n1a_alpha/positive" \
  "${ROOT}/a1_probe/n1a_alpha/negative" \
  "${ROOT}/a1_sign_scan/k0" \
  "${ROOT}/a1_sign_scan/n1a_alpha_0p5" \
  "${ROOT}/a1_sign_scan/n1a_alpha_2p0" \
  "${ROOT}/a1_sign_scan_asym_p/k0" \
  "${ROOT}/a1_sign_scan_asym_p/n1a_alpha_0p5" \
  "${ROOT}/a1_sign_scan_asym_p/n1a_alpha_2p0" \
  "${ROOT}/m2/k0/abs" \
  "${ROOT}/m2/k0/positive" \
  "${ROOT}/m2/k0/negative" \
  "${ROOT}/m2/n0/abs" \
  "${ROOT}/m2/n0/positive" \
  "${ROOT}/m2/n0/negative" \
  "${ROOT}/m2/n1a_alpha_0p5/abs" \
  "${ROOT}/m2/n1a_alpha_0p5/positive" \
  "${ROOT}/m2/n1a_alpha_0p5/negative" \
  "${ROOT}/m2/n1a_alpha_2p0/abs" \
  "${ROOT}/m2/n1a_alpha_2p0/positive" \
  "${ROOT}/m2/n1a_alpha_2p0/negative" \
  "${ROOT}/m2/comparisons"

# Add README placeholders so the tree is self-explanatory.
cat > "${ROOT}/README.md" <<'EOF'
# Results tree

Main blocks currently covered:

- k0: reference runs
- n0: null-model runs and ensembles
- n1a: wrong-dispersion controls
- n1a_scan: shared-theta scans and interval maps
- t1: theta-axis comparison outputs
- a1_probe: first sign-preserving probe
- a1_sign_scan: sign-preserving regime scans
- a1_sign_scan_asym_p: sign-preserving scans with asymmetrical p-sets
- m2: threshold-free weighted measures
EOF

cat > "${ROOT}/m2/comparisons/README.md" <<'EOF'
Expected comparison files here:
- m2_weighted_measures.csv
- m2_weighted_measures.json
- m2_summary.txt
EOF

cat > "${ROOT}/a1_sign_scan/README.md" <<'EOF'
This block stores sign-preserving scans for:
- k0
- n1a_alpha_0p5
- n1a_alpha_2p0

Each theta value is expected to contain:
- abs
- positive
- negative
EOF

cat > "${ROOT}/a1_sign_scan_asym_p/README.md" <<'EOF'
This block stores sign-preserving scans with asymmetrical p-sets.
Run-specific theta folders are expected below each case.
EOF

echo
echo "Done."
echo "Top-level folders created:"
find "${ROOT}" -maxdepth 1 -mindepth 1 -type d | sort
