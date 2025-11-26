# Phase 0: Research & Technical Decisions

**Feature**: DataLab Financial Analysis Platform
**Date**: 2025-11-26
**Status**: Completed

## Research Areas

### 1. Async WebSocket Client & Concurrency
**Context**: FR-001 requires concurrent connections. FR-032 requires resilient reconnection.
**Options**:
- **A (Recommended)**: `aiohttp`. Unified async HTTP/WebSocket client. Mature, widely used, supports complex timeout/retry logic.
- **B**: `websockets`. Lightweight, focused solely on WS.
- **C**: `ccxt`. Full exchange abstraction library. Rejected based on FR-008/FR-010 implying custom lightweight abstraction and specific "StandardizedTick" format.

**Decision**: **Option A (aiohttp)**.
**Rationale**: Reduces dependency count as HTTP will likely be needed for fetching historical data (FR-028/TradingView) or fallback snapshots. Excellent `asyncio` integration for handling the "Retry infini" requirement.

### 2. In-Memory Data Buffering
**Context**: FR-004 requires buffering 100,000 ticks (~100MB). SC-002 requires sub-100ms latency.
**Options**:
- **A (Recommended)**: `collections.deque` with `maxlen`. O(1) append/pop. Native Python objects (dict or dataclass).
- **B**: `numpy` pre-allocated arrays. Fast for numerical ops, but rigid for structured data with metadata strings (Exchange names).
- **C**: `pandas` DataFrame append. O(N) copy on append - too slow for realtime.

**Decision**: **Option A (collections.deque)** of `dataclass` objects.
**Rationale**: `deque` handles the rolling window naturally. Conversion to DataFrame/Parquet can happen asynchronously on flush. The ~100MB constraint is easily managed with 100k objects (approx 1KB/object is generous, actual likely <200B).

### 3. Parquet Storage Strategy
**Context**: FR-005 requires automatic timestamped filenames. FR-027 requires local caching.
**Options**:
- **A (Recommended)**: Batch Flush. Accumulate N ticks or T seconds, write immutable parquet file `data_{timestamp}.parquet`.
- **B**: Stream Write. Keep file open, append row groups. High risk of corruption on crash.
- **C**: Single File Update. Read-Write-Overwrite. Poor performance.

**Decision**: **Option A (Batch Flush)**.
**Rationale**: Simplifies "automatic timestamped filenames". specific requirement. Safer for data integrity. Easy to read back using `pandas.read_parquet(glob_pattern)`.

### 4. Project Structure
**Context**: Monorepo, Python, multiple modules (collector, backtest, strategy).
**Options**:
- **A (Recommended)**: `src/datalab/` package structure. Standard Python.
- **B**: Flat root. Messy.

**Decision**: **Option A**.
**Rationale**: Supports `pip install -e .` and clean imports (`from datalab.collector import ...`).

## Resolved Unknowns

- **Language**: Python 3.10 (Stable, modern type hinting).
- **Dependencies**: `aiohttp`, `pandas`, `numpy`, `pyarrow`, `plotly`.
- **Testing**: `pytest`, `pytest-asyncio`.
