from pathlib import Path

content = Path("src/serving/export.py").read_text()
content = content.replace("export = cast(Callable[[Any, tuple], Any], torch.export.export)", "export = cast(Callable[[Any, tuple[Any, ...]], Any], torch.export.export)")
Path("src/serving/export.py").write_text(content)

content = Path("src/models/bert.py").read_text()
content = content.replace("evaluation_strategy=\"epoch\"", "eval_strategy=\"epoch\"")
Path("src/models/bert.py").write_text(content)
