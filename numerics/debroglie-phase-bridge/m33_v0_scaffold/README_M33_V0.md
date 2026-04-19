# M33 / V0 scaffold

## Layout
- src/: python modules
- configs/: yaml configs
- scripts/: helper shell scripts
- runs/: output runs

## Expected core files
- src/config_schema.py
- src/columns_m33_v0.py
- src/m33_v0_runner.py
- configs/config_m33_v0.yaml

## Typical usage
python src/m33_v0_runner.py --project-root . --config configs/config_m33_v0.yaml
