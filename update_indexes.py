import json
from pathlib import Path


def title_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace("-", " ").replace("_", " ").title()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def is_subject_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    if path.name.startswith("."):
        return False
    return (path / "index.html").exists() or (path / "index.json").exists()


def update_subject_index(subject_dir: Path) -> bool:
    index_json_path = subject_dir / "index.json"
    existing = load_json(index_json_path)
    existing_resources = {
        r.get("file"): r for r in existing.get("resources", []) if isinstance(r, dict)
    }

    html_files = sorted(
        [
            p.name
            for p in subject_dir.glob("*.html")
            if p.name.lower() != "index.html"
        ]
    )

    resources = []
    for filename in html_files:
        prev = existing_resources.get(filename, {})
        resources.append(
            {
                "title": prev.get("title") or title_from_filename(filename),
                "file": filename,
                "description": prev.get("description", ""),
            }
        )

    subject_name = existing.get("subject") or subject_dir.name.replace("-", " ").title()
    output = {**existing, "subject": subject_name, "resources": resources}

    index_json_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    return True


def main() -> None:
    root = Path(__file__).resolve().parent
    subject_dirs = [p for p in root.iterdir() if is_subject_dir(p)]
    if not subject_dirs:
        print("No subject folders found.")
        return

    updated = 0
    for subject_dir in sorted(subject_dirs, key=lambda p: p.name):
        if update_subject_index(subject_dir):
            updated += 1
    print(f"Updated {updated} index.json file(s).")


if __name__ == "__main__":
    main()
