"""Shared slug helper for pv-internal-doc-features. Not invoked directly."""
import re
import unicodedata


def slugify(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def github_anchor(heading_text):
    """Replicates GitHub's anchor algorithm (to rewrite #anchor links in a legacy markdown)."""
    text = heading_text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = text.replace(" ", "-")
    return text
