"""Check the catalog, or just the files a pull request changes.

    python scripts/validate_catalog.py                     # every file
    python scripts/validate_catalog.py --changed-from REF  # files changed since REF (pull requests)

Exits 1 on any error. Warnings (emails, local paths ...) are printed for the
reviewer but don't fail the check. The rules live in scripts/catalog_rules.py,
an identical copy of the desktop app's agents/data_agent/catalog_rules.py.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if "--root" in sys.argv:  # checker run from outside the repo (pull requests use main's copy)
    ROOT = Path(sys.argv[sys.argv.index("--root") + 1]).resolve()
sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog_rules as rules  # noqa: E402

# A submission may only touch catalog files. Changes elsewhere are fine from the
# owner, but are flagged so they are never merged by accident from a contributor.
OWNER_ONLY_PREFIXES = (".github/", "scripts/", "README.md", "CONTRIBUTING.md", ".gitattributes")


def changed_files(ref):
    out = subprocess.run(["git", "diff", "--name-status", "--no-renames", f"{ref}...HEAD"],
                         cwd=ROOT, check=True, capture_output=True, text=True).stdout
    files = []
    for line in out.splitlines():
        status, path = line.split("\t", 1)
        files.append((status, path.replace("\\", "/")))
    return files


def annotate(level, path, msg):
    # GitHub Actions shows these inline on the pull request's "Files changed" tab.
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{level} file={path}::{msg}")
    else:
        print(f"{level.upper()}: {path}: {msg}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed-from", help="git ref to compare against (pull requests)")
    ap.add_argument("--root", help="catalog checkout to check (default: this script's repo)")
    args = ap.parse_args()

    if args.changed_from:
        targets = [(s, p) for s, p in changed_files(args.changed_from)]
    else:
        targets = [("M", p.relative_to(ROOT).as_posix())
                   for p in sorted((ROOT / "handbooks").glob("*")) + sorted((ROOT / "keys").glob("*"))]

    errors = warnings = 0
    checked = 0
    for status, path in targets:
        kind, slug = rules.classify_path(path)
        if kind is None:
            if path.startswith(("handbooks/", "keys/")):
                annotate("error", path, "only handbooks/<name>.toml and keys/<name>.keys belong in these folders")
                errors += 1
            elif path.startswith(OWNER_ONLY_PREFIXES) or args.changed_from:
                annotate("warning", path, "this file is outside the catalog; data-source submissions "
                                          "should only change handbooks/ and keys/")
                warnings += 1
            continue
        if status == "D":
            annotate("warning", path, "removes this source from the catalog for every user")
            warnings += 1
            continue
        data = (ROOT / path).read_bytes()
        check = rules.check_handbook if kind == "handbook" else rules.check_keys
        errs, warns = check(slug, data)
        if kind == "keys" and not (ROOT / "handbooks" / f"{slug}.toml").exists():
            errs.append(f"has no matching handbooks/{slug}.toml")
        for e in errs:
            annotate("error", path, e)
        for w in warns:
            annotate("warning", path, w)
        errors += len(errs)
        warnings += len(warns)
        checked += 1

    print(f"\nChecked {checked} catalog file(s): {errors} error(s), {warnings} warning(s).")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
