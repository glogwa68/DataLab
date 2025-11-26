import json
import os
from typing import Dict, Any

class ConfigError(Exception):
    pass

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load and validate configuration from a JSON file.
    """
    if not os.path.exists(config_path):
        raise ConfigError(f"Config file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file: {e}")

    _validate_config(config)
    return config

def _validate_config(config: Dict[str, Any]):
    """
    Basic schema validation.
    """
    if "collector" not in config:
        raise ConfigError("Missing required section: 'collector'")
    
    collector = config["collector"]
    if not isinstance(collector, dict):
        raise ConfigError("'collector' must be a dictionary")
    
    if "exchanges" in collector:
        if not isinstance(collector["exchanges"], list):
            raise ConfigError("'collector.exchanges' must be a list")
        
        for i, exchange in enumerate(collector["exchanges"]):
            if "name" not in exchange:
                raise ConfigError(f"Exchange at index {i} missing 'name'")
            if "symbols" not in exchange:
                raise ConfigError(f"Exchange at index {i} missing 'symbols'")
            if not isinstance(exchange["symbols"], list):
                raise ConfigError(f"Exchange '{exchange.get('name')}' symbols must be a list")

    # Set defaults if missing (though usually this is done by the consumer or a proper schema lib)
    # Here we just validate structure.
