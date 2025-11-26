import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from typing import List, Any
import os
from datetime import datetime

def save_to_parquet(data: List[Any], filepath: str, compression: str = 'snappy'):
    """
    Save a list of dataclass objects or dictionaries to a Parquet file.
    
    Args:
        data: List of objects to save.
        filepath: Destination path.
        compression: Compression codec (default: 'snappy').
    """
    if not data:
        return

    df = pd.DataFrame([d.__dict__ if hasattr(d, '__dict__') else d for d in data])
    
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    table = pa.Table.from_pandas(df)
    pq.write_table(table, filepath, compression=compression)

def load_from_parquet(filepath: str) -> pd.DataFrame:
    """
    Load data from a Parquet file into a DataFrame.
    """
    return pd.read_parquet(filepath)

def get_timestamped_filename(prefix: str = "data", extension: str = "parquet") -> str:
    """Generate a filename with current timestamp (nanoseconds)."""
    timestamp = int(datetime.now().timestamp() * 1e9)
    return f"{prefix}_{timestamp}.{extension}"
