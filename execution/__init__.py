from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from .mt5_client import MT5Client

_root_execution_path = Path(__file__).resolve().parent.parent / "execution.py"
if _root_execution_path.exists():
    _spec = spec_from_file_location("_legacy_execution", _root_execution_path)
    if _spec and _spec.loader:
        _legacy = module_from_spec(_spec)
        _spec.loader.exec_module(_legacy)
        executer_ordre = _legacy.executer_ordre

__all__ = ["MT5Client", "executer_ordre"]
