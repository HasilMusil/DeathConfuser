"""Entry point for DeathConfuser framework."""
from __future__ import annotations

import sys
from pathlib import Path


if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from DeathConfuser.interface.cli import main  # type: ignore
else:  # pragma: no cover - executed when run as module
    from .interface.cli import main


if __name__ == "__main__":
    main()
