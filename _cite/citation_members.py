"""Preserve every member association when duplicate citations are merged."""


def has_verified_metadata(source):
    """Only a complete, explicitly reviewed citation can skip online lookup."""
    return (
        source.get("metadata_verified") is True
        and all(isinstance(source.get(key), str) and source[key].strip()
                for key in ("title", "publisher", "date", "link"))
        and isinstance(source.get("authors"), list)
        and bool(source["authors"])
        and all(isinstance(author, str) and author.strip() for author in source["authors"])
        and isinstance(source.get("verification"), dict)
        and bool(source["verification"].get("sources"))
    )


def citation_orcids(source):
    values = source.get("orcids") or []
    if isinstance(values, str):
        values = [values]
    values = [*values, source.get("orcid")]
    return list(dict.fromkeys(
        value.strip().upper() for value in values
        if isinstance(value, str) and value.strip()
    ))


def merge_sources(sources):
    """Later metadata wins; membership is a union, including manual overrides."""
    merged = []
    by_id = {}
    for source in sources:
        source = dict(source)
        orcids = citation_orcids(source)
        if orcids:
            source["orcids"] = orcids
        identifier = (source.get("id") or "").strip()
        # DOI case does not distinguish papers. Keep other identifier types intact.
        key = identifier.lower() if identifier.lower().startswith("doi:") else identifier
        if key and key in by_id:
            previous = by_id[key]
            orcids = list(dict.fromkeys(citation_orcids(previous) + orcids))
            previous.update(source)
            if orcids:
                previous["orcids"] = orcids
        else:
            merged.append(source)
            if key:
                by_id[key] = source
    return merged
