import hashlib
import re

from config import BOOKS_SOURCE


def normalize(value):
    value = re.sub(r"[^\w\s]", "", (value or "").lower())
    return " ".join(value.split())


def make_fingerprint(rec):
    parts = [normalize(rec.get("source"))]
    if rec.get("source") == BOOKS_SOURCE:
        parts.append(normalize(rec.get("name_or_title")))
    else:
        parts.append(normalize(rec.get("author")))
        parts.append(normalize(rec.get("name_or_title"))[:50])
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def find_duplicates(records):
    seen, unique, dupes = set(), [], []
    for rec in records:
        fingerprint = make_fingerprint(rec)
        if fingerprint in seen:
            dupes.append(rec)
        else:
            seen.add(fingerprint)
            unique.append(rec)
    return unique, dupes
