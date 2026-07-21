"""Entry point for the complete PIA platform showcase."""

from __future__ import annotations

import sys
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

from .pipeline import PlatformPipeline


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()


def main() -> None:
    pipeline = PlatformPipeline()
    pipeline.run()


def run_and_save() -> None:
    output_dir = Path(__file__).resolve().parents[1] / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"platform_showcase_{timestamp}.txt"

    error: BaseException | None = None

    with output_file.open("w", encoding="utf-8") as file:
        try:
            with redirect_stdout(Tee(sys.stdout, file)):
                main()
        except BaseException as exc:
            error = exc

    print(f"\nOutput saved to: {output_file}")

    if error is not None:
        raise error


if __name__ == "__main__":
    run_and_save()
