from pathlib import Path

content = Path("src/serving/export.py").read_text()
content = content.replace("torch.export.export", "torch.jit.trace")
Path("src/serving/export.py").write_text(content)
