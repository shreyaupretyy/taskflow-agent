"""Helper functions for data transformation."""
from typing import Any, Dict, List
import json


def dict_to_flat(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(dict_to_flat(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def flat_to_dict(d: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """Convert a flat dictionary to nested."""
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def filter_dict(d: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Filter dictionary by keys."""
    return {k: v for k, v in d.items() if k in keys}


def exclude_dict_keys(d: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Exclude keys from dictionary."""
    return {k: v for k, v in d.items() if k not in keys}


def safe_json_loads(s: str, default: Any = None) -> Any:
    """Safely load JSON with default value."""
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = '{}') -> str:
    """Safely dump JSON with default value."""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return default
