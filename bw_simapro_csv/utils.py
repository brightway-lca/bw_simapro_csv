def clean(s: str) -> str:
    """Strip string and remove ASCII delete character"""
    return s.replace("\x7f", "").strip()


def nobraces(s: str) -> str:
    """Remove braces from header section elements"""
    return s[2:-2] if s.startswith('"{') else s[1:-1]


def noquotes(s: str) -> str:
    """Remove string start/end characters"""
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def asboolean(s: str) -> bool:
    """Convert SimaPro strings to actual booleans"""
    if s.lower() in {"yes", "y", "true", "t", "1"}:
        return True
    if s.lower() in {"no", "n", "false", "f", "0"}:
        return False
    # Better raise an error then assume we understand SimaPro
    raise ValueError(f"Can't convert '{s}' to boolean")
