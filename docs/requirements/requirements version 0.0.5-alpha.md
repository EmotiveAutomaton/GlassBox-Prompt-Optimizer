# Multi-Dataset Optimization Requirements

## Overview
Enable the GlassBox Prompt Optimizer to validate prompt candidates against multiple distinct test datasets simultaneously, ensuring robust performance across diverse inputs.

## Core Functional Requirements

### 1. Data Ingestion (Zone A)
-   **Multiple Datasets**: Users must be able to upload multiple distinct test files (tabbed interface).
-   **Persistence**: Datasets must persist in session state until explicitly deleted.
-   **Visibility**: File names and metadata must be visible in the "Test Data" card.
-   **Active Selection**: Users can switch tabs to view/edit specific datasets.

### 2. Optimization Engine (Backend)
-   **Execution Loop**: The `Evaluator` must run the candidate prompt against **ALL** active datasets in the current session.
-   **Scoring Logic**:
    -   Individual Score: Calculate score for each dataset result.
    -   Aggregate Score: Calculate the **Arithmetic Mean** (Average) of all individual scores.
-   **Stopping Condition**: Use the *Aggregate Score* for threshold checks.
-   **Performance**: Should handle N datasets (sequential or parallel, TBD based on API limits).

### 3. Results Visualization (Zone C)
-   **Dynamic Table Layout**:
    -   **Single Dataset Mode**: Columns: `[Score] [Iter] [Prompt Candidate] [Result]`
    -   **Multi-Dataset Mode**: Columns: `[Avg Score] [Iter] [Prompt Candidate] | [Result 1] [Score 1] | [Result 2] [Score 2] ...`
-   **Data Consistency**: Ensure row counts match optimization steps (no duplicates).
-   **Sorting**: Sorting by "Avg Score" should sort the rows globally.

### 4. Graph Visualization (Glass Box)
-   **Metric**: The graph must plot the **Aggregate/Average Score**.
-   **Tooltips**: Hovering a node should show the prompt and the Avg Score (and optionally breakdown if space permits).

### 5. Interaction
-   **Delete Safety**: Deleting a dataset must prompt for confirmation (Modal) and not shift layout.
-   **State Sync**: Deleting a dataset implies recalculating "Avg Score" for *future* runs (past runs remain historical).

## Failure Modes to Avoid (Lessons Learned)
-   **Score 100 Glitch**: Ensuring the loop doesn't prematurely exit or mock perfect scores.
-   **Iteration Count Desync**: Generating 1 result but logging it as multiple iterations.
-   **Layout Shift**: Dynamic columns pushing UI elements out of bounds.
