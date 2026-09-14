from pathlib import Path

content = Path("src/serving/export.py").read_text()
content = content.replace("trace = cast(Callable[[Any, Any], Any], torch.jit.trace)", "export = cast(Callable[[Any, tuple], Any], torch.export.export)")
content = content.replace("scripted = trace(model, example_inputs)", "if not isinstance(example_inputs, tuple):\n        example_inputs = (example_inputs,)\n    scripted = export(model, example_inputs)")
content = content.replace("scripted.save(str(output))", "torch.export.save(scripted, str(output))")
Path("src/serving/export.py").write_text(content)
