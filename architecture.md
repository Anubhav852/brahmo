# Brahmo Clinical Pipeline Architecture

## Overview
The Brahmo Pipeline is a deterministic, context-aware system designed to deliver clinical decision support content while strictly adhering to internal compliance and department-level isolation policies. The system architecture avoids non-deterministic models (LLMs) in favor of a rule-based engine to ensure 100% auditability and safety in clinical settings.

## 1. Core Traversal Engine (BFS)
To navigate the complex clinical Knowledge Graph, the system uses a **Breadth-First Search (BFS)** traversal.
* **Mechanism:** Starting from a user-provided `entry_node`, the system traverses the Directed Acyclic Graph (DAG) upward.
* **Why BFS?** BFS explores the graph in "layers" of relevance, ensuring that immediate ancestor nodes are processed first.
* **Complexity:** By maintaining a `visited` set, the traversal achieves $O(V+E)$ efficiency, preventing infinite loops in cyclic graph scenarios and redundant database calls.

## 2. The 5-Check Sequential Filter Pipeline
Once the initial node pool is identified, the system passes candidates through a sequential filtering pipeline. This "fail-fast" approach ensures that computationally expensive checks are only performed on nodes that have already passed initial safety filters.

| Stage | Filter | Rationale |
| :--- | :--- | :--- |
| 1 | Department Isolation | Removes content outside the user's clinical specialty. |
| 2 | Temporal Validity | Filters out nodes whose clinical guidelines have expired. |
| 3 | Compliance/MNPI | Blocks nodes containing sensitive patient information. |
| 4 | Derivability | Excludes "General Knowledge" nodes that lack clinical value. |
| 5 | User Constraints | Applies user-specific clearance and seniority rules. |

## 3. Pipeline Transparency & Auditability
To maintain system trust, the pipeline exposes its internal state via a `funnel_stats` object. This object provides a real-time count of surviving nodes at each stage of the filtering pipeline. 



## 4. Deterministic Contextual Delivery
The system is built to be context-aware rather than static. By accepting `user_id` as a primary parameter, the backend re-executes the pipeline dynamically for each session. This ensures that:
* Two different users (e.g., a Resident and an Attending Physician) viewing the same entry node receive different, policy-compliant results.
* The output is reproducible, allowing for rigorous clinical safety auditing.

## 5. Technology Stack
* **Backend:** FastAPI (Python) for asynchronous request handling.
* **Database:** Supabase (PostgreSQL) for graph storage and relational node data.
* **Frontend:** React for reactive state management and dynamic dashboard visualization.