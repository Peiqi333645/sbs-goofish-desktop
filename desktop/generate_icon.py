from pathlib import Path
import cairosvg

HERE = Path(__file__).resolve().parent
source = HERE / "build" / "icon.svg"
target = HERE / "build" / "icon.png"
target.parent.mkdir(parents=True, exist_ok=True)
cairosvg.svg2png(url=str(source), write_to=str(target), output_width=1024, output_height=1024)
print(f"Generated {target}")
