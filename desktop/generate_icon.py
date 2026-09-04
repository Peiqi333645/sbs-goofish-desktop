"""Generate the desktop PNG from the single user-approved icon master."""
from pathlib import Path

from PIL import Image


here = Path(__file__).resolve().parent
source = here / "build" / "icon-master.png"
target = here / "build" / "icon.png"

if not source.exists():
    raise SystemExit(f"Missing icon master: {source}")

with Image.open(source) as original:
    icon = original.convert("RGBA")
    if icon.width != icon.height:
        raise SystemExit("Icon master must be square")
    icon.resize((1024, 1024), Image.Resampling.LANCZOS).save(
        target,
        "PNG",
        optimize=True,
    )

print(f"Generated {target} from {source}")
