#!/bin/bash -eu

# ClusterFuzzLite's Python builder pre-installs Atheris and PyInstaller. Install
# only parser dependencies from the reviewed Linux/Python 3.11 hash lock; no
# raw article text, datasets, or model artifacts are copied to fuzzer output.
python3 -m pip install --no-cache-dir --require-hashes --only-binary=:all: \
  -r requirements/locks/fuzz-py311-manylinux_2_28.txt

TARGET="$SRC/fake-news-detection/fuzz/atheris_claimreview_fuzzer.py"
pyinstaller --distpath "$OUT" --onefile --name atheris_claimreview_fuzzer.pkg "$TARGET"

cat > "$OUT/atheris_claimreview_fuzzer" <<'EOF'
#!/bin/sh
# LLVMFuzzerTestOneInput
this_dir=$(dirname "$0")
exec "$this_dir/atheris_claimreview_fuzzer.pkg" "$@"
EOF
chmod +x "$OUT/atheris_claimreview_fuzzer"
