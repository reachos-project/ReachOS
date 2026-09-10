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
-- The two axes are stored separately because they decide differently: the structural axis is
-- all-or-nothing (any failed item blocks), the content axis is a number that governs REVIEW
-- vs SHIP. A single total cannot express "12/12 with one blocker". See docs/04-quality-gate.md.
CREATE TABLE deliverables (
    id                INTEGER PRIMARY KEY,
    task_id           INTEGER REFERENCES tasks(id),
    filepath          TEXT,
    deliverable_type  TEXT,
    structural_score  INTEGER,   -- 0..9  passed structural items
    content_score     INTEGER,   -- 0..3  passed content items
    blockers          INTEGER,   -- count of failed structural items; >0 => FIX FIRST
    quality_score     INTEGER,   -- 0..12 convenience total = structural + content
    revision_rounds   INTEGER,
    user_rating       INTEGER,   -- 1..10, optional
    tags              TEXT,      -- JSON array
    created_at        TEXT NOT NULL
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

-- Clocks: one-shot dated items, each carrying a QUESTION. A clock dies when answered.
-- The shelf (templates/ACTIVE.template.md) names the slug; the state lives here, never in prose.
-- State machine: armed -> acked -> retired. `acked` means a human saw it; `retired` means the
-- question has an answer. Skipping straight to retired loses the distinction between
-- "answered" and "dismissed", which is the whole point of storing it.
CREATE TABLE clocks (
    slug        TEXT PRIMARY KEY,     -- referenced from the active shelf
    question    TEXT NOT NULL,        -- what must be answered; not "check X" but "is X still true?"
    due_on      TEXT NOT NULL,        -- date only; a clock with no date is not a clock
    state       TEXT NOT NULL,        -- armed | acked | retired
    armed_at    TEXT NOT NULL,
    acked_at    TEXT,                 -- when a human acknowledged it fired
    retired_at  TEXT,                 -- when the question was answered
    answer      TEXT                  -- the answer itself; NULL while state != 'retired'
);

-- Routines: recurring practices. A routine is never "done" — only this period's occurrence is.
CREATE TABLE routines (
    id                TEXT PRIMARY KEY,   -- referenced from the active shelf
    practice          TEXT NOT NULL,      -- what recurs
    cadence_days      INTEGER NOT NULL,
    completion_action TEXT,               -- the logged action whose presence PROVES it ran
    armed_since       TEXT NOT NULL,      -- first successful fire; misses before this are not misses
    reminded_at       TEXT,               -- written by the scheduler, when it enqueues
    completed_at      TEXT,               -- written by the session, when the work happened
    -- How far this routine may act unattended. Classified by what it EXECUTES, not by its
    -- most dangerous step (docs/09). A routine widened from reading to writing changes class.
    autonomy_class    TEXT NOT NULL DEFAULT 'ask-first'
                      CHECK (autonomy_class IN ('measure-only','propose-and-hold','ask-first')),
    -- A propose-and-hold routine produces a verdict that nobody may act on but the person.
    -- Store it, or it lives only in the log and is never read (docs/09).
    last_conclusion    TEXT,
    last_conclusion_at TEXT
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


-- ---------------------------------------------------------------------------
-- Seed data — the minimum that makes the worked example resolvable.
-- Without these rows, two of the four anchor kinds the sweep classifies
-- (clock-slug, routine-id) resolve to nothing, and the reference instance
-- cannot demonstrate its own sweep.
-- ---------------------------------------------------------------------------

INSERT INTO clocks (slug, question, due_on, state, armed_at) VALUES
  ('q4-client-deck',
   'Is the client deck delivered?',
   '2026-09-12', 'armed', '2026-08-20'),
  ('vendor-contract-renewal',
   'Renew, renegotiate, or let it lapse?',
   '2026-10-01', 'armed', '2026-09-01');

INSERT INTO routines (id, practice, cadence_days, completion_action, armed_since,
                      autonomy_class) VALUES
  ('market_brief_weekly',
   'Monday market brief for the active pipeline',
   7, 'market_brief_written', '2026-07-14', 'measure-only'),
  ('pipeline_hygiene',
   'Reconcile pipeline records against reality; propose closures',
   14, 'pipeline_hygiene_swept', '2026-08-04', 'propose-and-hold');
