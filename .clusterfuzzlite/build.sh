#!/bin/bash -eu

# ClusterFuzzLite's Python builder pre-installs Atheris and PyInstaller. Install
# only parser dependencies are installed; no raw article text, datasets, or model artifacts are copied to fuzzer output.
python3 -m pip install --no-cache-dir \
  "pandas==2.2.3" \
  "scikit-learn==1.5.2" \
  "ijson==3.3.0" \
  "pyyaml==6.0.2"

TARGET="$SRC/fake-news-detection/fuzz/atheris_claimreview_fuzzer.py"
pyinstaller --distpath "$OUT" --onefile --name atheris_claimreview_fuzzer.pkg "$TARGET"

cat > "$OUT/atheris_claimreview_fuzzer" <<'EOF'
#!/bin/sh
# LLVMFuzzerTestOneInput
this_dir=$(dirname "$0")
exec "$this_dir/atheris_claimreview_fuzzer.pkg" "$@"
EOF
chmod +x "$OUT/atheris_claimreview_fuzzer"
