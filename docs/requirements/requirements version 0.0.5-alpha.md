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
-   **Conditional Table Layout**:
    -   **Single Dataset Mode**: Columns: `[Score] [Iter] [Prompt Candidate] [Result]` (Classic View).
    -   **Multi-Dataset Mode**: Columns: `[Avg Score (Wide)] [Iter] [Prompt Candidate] [Score 1] [Score 2] ... [Score N]`.
        -   *Note:* Result text is hidden in the table to conserve space; viewed in Zone E.
-   **Interaction**:
    -   **Row Selection**: Clicking a row highlights it (Dark Blue).
    -   **Multi-Select**: Users can select up to 2 rows.
    -   **Focus Toggle**: Clicking the currently active (Dark Blue) row clears the secondary selection, isolating the active row.

### 4. Detail Inspection & Diff (Zone E)
*Replaces "Test Bench Inputs" (now in Zone A).*
-   **Mode 1: Single Selection (Detail View)**
    -   **Layout**: split 25/75.
    -   **Left Pane**: List of Datasets (selectable).
    -   **Right Pane**:
        -   Header: Iteration #, Aggregate Score.
        -   Content: Full **Prompt Text** and **Result Text** for the dataset selected in Left Pane.
-   **Mode 2: Dual Selection (Diff View)**
    -   **Trigger**: When two rows are selected in Zone C.
    -   **Content**: Visual Text Diff of the **Prompt Candidates**.
    -   **Styling**:
        -   **Additions**: Muted Green background.
        -   **Deletions**: Muted Red background (strikethrough).
    -   **Goal**: Highlight exactly what changed between the two iterations.
