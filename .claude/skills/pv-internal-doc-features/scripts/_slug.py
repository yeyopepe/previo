"""Helper compartido de slugs para ms-internal-doc-features. No se invoca directamente."""
import re
import unicodedata


def slugify(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def github_anchor(heading_text):
    """Replica el algoritmo de anclas de GitHub (para reescribir enlaces #ancla de un markdown legado)."""
    text = heading_text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = text.replace(" ", "-")
    return text
