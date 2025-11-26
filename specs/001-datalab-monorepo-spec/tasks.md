# Tasks: DataLab Financial Analysis Platform

**Feature**: DataLab Monorepo
**Status**: Planned
**Spec**: `specs/001-datalab-monorepo-spec/spec.md`

## Phase 1: Setup

**Goal**: Initialize project structure and development environment.

- [x] T001 Create project configuration (pyproject.toml) with dependencies in `pyproject.toml`
- [x] T002 Create src directory structure (datalab/collector, datalab/strategy, etc.) in `src/datalab/`
- [x] T003 Create test directory structure (unit, integration) in `tests/`
- [x] T004 [P] Create initial README with usage instructions in `README.md`

## Phase 2: Foundational

**Goal**: Implement shared utilities and base classes required by all user stories.

- [x] T005 [P] Create storage utility for Parquet operations (Snappy compression) in `src/datalab/utils/storage.py`
- [x] T006 [P] Implement config loading and schema validation in `src/datalab/utils/config.py`
- [x] T007 Create Exchange abstract base class and StandardizedTick dataclass in `src/datalab/collector/exchange.py`
- [x] T008 Create BaseDCAStrategy abstract base class in `src/datalab/strategy/base.py`
- [x] T009 Create CLI entry point skeleton with click/argparse in `src/datalab/cli.py`

## Phase 3: User Story 1 - Collect and Compare DEX Data (P1)

**Goal**: Enable real-time data collection from multiple exchanges.
**Independent Test**: Verify connection, buffering, and parquet export using `tests/integration/test_collector.py`.

- [x] T010 [P] [US1] Create unit tests for Exchange base class and MockExchange in `tests/unit/test_exchange.py`
- [x] T011 [P] [US1] Implement dYdX exchange client in `src/datalab/collector/clients/dydx.py`
- [x] T012 [P] [US1] Implement Binance exchange client in `src/datalab/collector/clients/binance.py`
- [x] T013 [US1] Create unit tests for MultiExchangeCollector in `tests/unit/test_manager.py`
- [x] T014 [US1] Implement MultiExchangeCollector with buffering logic in `src/datalab/collector/manager.py`
- [x] T015 [US1] Implement 'collect' command in CLI in `src/datalab/cli.py`
- [x] T016 [US1] Create integration test for full collection workflow in `tests/integration/test_collector.py`

## Phase 4: User Story 2 - Backtest DCA Strategies (P1)

**Goal**: Enable historical backtesting of investment strategies.
**Independent Test**: Run backtest with known data and verify TWR/metrics match expected values.

- [x] T017 [US2] Create unit tests for Backtest Engine in `tests/unit/test_backtest.py`
- [x] T018 [US2] Implement BacktestResult dataclass and metrics calculation in `src/datalab/backtest/engine.py`
- [x] T019 [US2] Implement core backtesting loop and logic in `src/datalab/backtest/engine.py`
- [x] T020 [P] [US2] Implement standard periodic DCA strategy in `src/datalab/strategy/library/dca.py`
- [x] T021 [P] [US2] Implement 'backtest' command in CLI in `src/datalab/cli.py`
- [x] T022 [US2] Create integration test for backtest workflow in `tests/integration/test_backtest.py`

## Phase 5: User Story 3 - Real-Time Market Monitoring (P2)

**Goal**: Add alerting capabilities to the collector.
**Independent Test**: Simulate spread threshold breach and verify log/alert output.

- [x] T023 [US3] Create unit tests for alerting logic in `tests/unit/test_alerts.py`
- [x] T024 [US3] Extend MultiExchangeCollector with threshold monitoring in `src/datalab/collector/manager.py`
- [x] T025 [US3] Update 'collect' command to accept threshold arguments in `src/datalab/cli.py`

## Phase 6: User Story 4 - Extend Exchange Coverage (P2)

**Goal**: Verify extensibility by adding a third exchange support.
**Independent Test**: Connect to new simulated/real exchange and verify standardized ticks.

- [x] T026 [US4] Implement Simulated/Hyperliquid exchange client in `src/datalab/collector/clients/hyperliquid.py`
- [x] T027 [US4] Register new exchange in factory/config in `src/datalab/collector/manager.py`
- [x] T028 [US4] Verify new exchange integration in `tests/integration/test_collector.py`

## Phase 7: User Story 5 - Custom DCA Strategies (P2)

**Goal**: Implement advanced strategy logic.
**Independent Test**: Run backtest with custom strategy and verify signal behavior.

- [x] T029 [US5] Implement Momentum-based DCA strategy in `src/datalab/strategy/library/momentum.py`
- [x] T030 [US5] Create unit tests for Momentum strategy signals in `tests/unit/test_momentum.py`

## Phase 8: Polish & Visualization

**Goal**: Finalize visualization and documentation.

- [x] T031 [P] Implement plotting utilities using Plotly (interactive only) in `src/datalab/analysis/plotting.py`
- [x] T032 Implement 'analyze' command in CLI in `src/datalab/cli.py`
- [x] T033 Create end-to-end usage guide in `docs/usage.md`

## Implementation Strategy

- **MVP Scope**: Phases 1, 2, and 3 (US1). This delivers the core value of collecting and comparing data.
- **Incremental Delivery**:
    - Deliver US1 (Collection) first to start gathering data.
    - Deliver US2 (Backtesting) next to analyze data.
    - Follow with P2 features (Monitoring, Extensions, Advanced Strategies).

## Dependencies

1. **Foundational**: T001-T009 must complete before any US tasks.
2. **US1 (Collector)**: Depends on T007 (Exchange ABC), T005 (Storage).
3. **US2 (Backtest)**: Depends on T008 (Strategy ABC), T005 (Storage for reading data).
4. **US3 (Monitoring)**: Extends US1, must come after T014.
5. **US4 (New Exchange)**: Extends US1, must come after T014.
6. **US5 (Custom Strategy)**: Extends US2, must come after T019.

## Parallel Execution Examples

- **Within Phase 3**: T011 (dYdX) and T012 (Binance) can be implemented in parallel by two developers once T007 (ABC) is ready.
- **Between Phases**: T020 (DCA Strategy) can be implemented in parallel with T014 (Collector) as they only share the Base Strategy dependency.
- **Documentation**: T033 can be started alongside Phase 3.