"""Splits a monolithic FEATURES.md ('## Area' / '### Feature' format) into one
file per feature inside a folder, rewriting internal cross-links ('#...'
anchors) into relative links between files, assigns each one a sequential
identifying number (per the order they appear in the original document), and
generates the final INDEX.md.

Usage (from the repo root):
    python migrate-legacy-features-doc.py --source design/docs/FEATURES.md --dest design/docs/features

Not an invocable skill -- a one-off utility to adopt the folder convention
in a project that already had a FEATURES.md as a single file.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from _slug import github_anchor, slugify

AREA_RE = re.compile(r"^##\s+(.+)$")
FEATURE_RE = re.compile(r"^###\s+(.+)$")


def parse_sections(text):
    lines = text.splitlines()
    area = None
    sections = []  # (area, title, body_lines)
    preamble = []
    current = None  # dict(title, body)

    def flush():
        if current is not None:
            sections.append((area, current["title"], "\n".join(current["body"]).strip()))

    for line in lines:
        m_area = AREA_RE.match(line)
        m_feat = FEATURE_RE.match(line)
        if m_area:
            flush()
            current = None
            area = m_area.group(1).strip()
            continue
        if m_feat:
            flush()
            current = {"title": m_feat.group(1).strip(), "body": []}
            continue
        if current is not None:
            current["body"].append(line)
        elif area is None:
            preamble.append(line)
        elif line.strip():
            raise SystemExit(f"Orphan content under area '{area}' with no feature: {line!r}")
    flush()
    return sections


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--dest", required=True)
    args = parser.parse_args()

    source = Path(args.source)
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    sections = parse_sections(source.read_text(encoding="utf-8"))

    width = max(len(str(len(sections))), 3)

    # the filename carries the number up front (same order as the index); the number
    # already guarantees uniqueness, so the title's slug doesn't need to be collision-safe itself.
    feature_ids = [str(n).zfill(width) for n in range(1, len(sections) + 1)]
    filenames = [f"{fid}-{slugify(title) or 'feature'}" for fid, (_, title, _) in zip(feature_ids, sections)]

    anchor_to_slug = {
        github_anchor(title): filename
        for (_, title, _), filename in zip(sections, filenames)
    }
    area_anchors = {github_anchor(area) for area, _, _ in sections}

    def rewrite_links(body):
        def repl(m):
            anchor = m.group(1)
            target = anchor_to_slug.get(anchor)
            if target is not None:
                return f"]({target}.md)"
            if anchor in area_anchors:
                return f"](INDEX.md#{anchor})"
            print(f"  warning: no target found for link #{anchor}", file=sys.stderr)
            return m.group(0)
        return re.sub(r"\]\(#([^)]+)\)", repl, body)

    for feature_id, filename, (area, title, body) in zip(feature_ids, filenames, sections):
        # splits the final "- **Available in**: ... / - **Code**: ..." block from the rest of the body
        body = rewrite_links(body)
        lines = [ln for ln in body.splitlines()]
        tail = []
        while lines and (lines[-1].strip() == "" or lines[-1].lstrip().startswith("- **")):
            tail.insert(0, lines.pop())
        available_in = next((ln.split(":", 1)[1].strip() for ln in tail if "**Available in**" in ln), "")
        code = next((ln.split(":", 1)[1].strip() for ln in tail if "**Code**" in ln), "")
        prose = "\n".join(lines).strip()

        content = (
            f"# {feature_id} — {title}\n\n"
            f"**Area**: {area}\n\n"
            f"{prose}\n\n"
            f"- **Available in**: {available_in}\n"
            f"- **Code**: {code}\n"
            f"- **Since**: (pending)\n"
            f"- **Last modified**: (pending)\n"
        )
        (dest / f"{filename}.md").write_text(content, encoding="utf-8")

    print(f"{len(sections)} features migrated to {dest}/")

    subprocess.run(
        [sys.executable, str(Path(__file__).parent / "rebuild-index.py"), "--folder", str(dest)],
        check=True,
    )


if __name__ == "__main__":
    main()
