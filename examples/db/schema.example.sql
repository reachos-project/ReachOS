-- schema.example.sql
-- The traceability nomenclature (procedural_memory, activity_history) is shared
-- with the upstream genesis (Apache-2.0) — see NOTICE. Conscious and attributed reproduction.
-- CONCEPTUAL and FICTIONAL data model of the transactional store that provides traceability
-- for the system (Rule 3). Serves as a reference — adapt to your database engine.
-- Contains no real data. Column names are illustrative.

-- Tasks delegated by the coordinator.
CREATE TABLE tasks (
    id              INTEGER PRIMARY KEY,
    title           TEXT NOT NULL,
    assigned_to     TEXT,                 -- agent slug
    status          TEXT NOT NULL,        -- open | in_progress | completed | cancelled
    result_summary  TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT
);

-- Audit trail of each delegation between the coordinator and agents.
CREATE TABLE interactions (
    id          INTEGER PRIMARY KEY,
    task_id     INTEGER REFERENCES tasks(id),
    from_actor  TEXT,                     -- e.g.: coordinator
    to_actor    TEXT,                     -- e.g.: agent slug
    summary     TEXT,
    created_at  TEXT NOT NULL
);

-- Registry of active agents.
CREATE TABLE agents (
    slug        TEXT PRIMARY KEY,
    display_name TEXT,
    role        TEXT,
    active      INTEGER DEFAULT 1
);

-- Deliverables handed to the user (feeds quality gate metrics).
CREATE TABLE deliverables (
    id                        INTEGER PRIMARY KEY,
    task_id                   INTEGER REFERENCES tasks(id),
    filepath                  TEXT,
    deliverable_type          TEXT,
    quality_score             INTEGER,    -- 1..12 (structural + content)
    revision_rounds INTEGER,
    user_rating  INTEGER,    -- 1..10, optional
    tags                      TEXT,       -- JSON array
    created_at                TEXT NOT NULL
);

-- Learned patterns (procedural memory) — success/failure by task type.
CREATE TABLE procedural_memory (
    id              INTEGER PRIMARY KEY,
    trigger_pattern TEXT,
    action          TEXT,
    success_count   INTEGER DEFAULT 0,
    fail_count      INTEGER DEFAULT 0,
    last_used       TEXT
);

-- Append-only activity history (audit and reversibility).
CREATE TABLE activity_history (
    id           INTEGER PRIMARY KEY,
    actor        TEXT,
    action       TEXT,
    entity_type  TEXT,
    entity_id    INTEGER,
    summary      TEXT,
    occurred_at  TEXT NOT NULL
);

-- Context health view (example aggregation for diagnostics).
CREATE VIEW v_system_health AS
SELECT
    (SELECT COUNT(*) FROM tasks WHERE status = 'open')        AS open_tasks,
    (SELECT COUNT(*) FROM agents WHERE active = 1)            AS active_agents,
    (SELECT COUNT(*) FROM deliverables)                       AS total_deliverables,
    (SELECT ROUND(AVG(quality_score), 2) FROM deliverables)   AS avg_quality_score;
