from pathlib import Path

content = Path("src/models/bert.py").read_text()
content = content.replace("eval_strategy=\"epoch\",", "eval_strategy=\"epoch\",")
content = content.replace("eval_strategy=\"epoch\"", "evaluation_strategy=\"epoch\"")
Path("src/models/bert.py").write_text(content)
