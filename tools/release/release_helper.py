# tools/release/release_helper.py
import subprocess, sys
from pathlib import Path

CHANGELOG = Path("tools/release/changelog_template.md")

def draft_release(version, date, notes_file=None):
    if not CHANGELOG.exists():
        print("No changelog found. Create tools/release/changelog_template.md first.")
        return 1
    msg = f"Release {version} - {date}\n\n"
    if notes_file and Path(notes_file).exists():
        msg += Path(notes_file).read_text()
    else:
        msg += CHANGELOG.read_text()
    tag = f"v{version}"
    subprocess.check_call(["git", "tag", "-a", tag, "-m", msg])
    print(f"Tag {tag} created. Push with `git push origin {tag}` and create GitHub release from tag.")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/release/release_helper.py <version> <YYYY-MM-DD>")
        sys.exit(2)
    sys.exit(draft_release(sys.argv[1], sys.argv[2]))