-- schema.example.sql
-- Nomenclatura de rastreabilidade (procedural_memory, activity_history) partilhada
-- com o upstream genesis (Apache-2.0) — ver NOTICE. Reprodução consciente e atribuída.
-- Modelo de dados CONCEPTUAL e FICTÍCIO do store transaccional que dá rastreabilidade
-- ao sistema (Regra 3). Serve de referência — adapta ao teu motor de base de dados.
-- Não contém dados reais. Os nomes de colunas são ilustrativos.

-- Tarefas delegadas pelo coordenador.
CREATE TABLE tasks (
    id              INTEGER PRIMARY KEY,
    title           TEXT NOT NULL,
    assigned_to     TEXT,                 -- slug do agente
    status          TEXT NOT NULL,        -- open | in_progress | completed | cancelled
    result_summary  TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT
);

-- Audit trail de cada delegação entre coordenador e agentes.
CREATE TABLE interactions (
    id          INTEGER PRIMARY KEY,
    task_id     INTEGER REFERENCES tasks(id),
    from_actor  TEXT,                     -- ex.: coordenador
    to_actor    TEXT,                     -- ex.: slug do agente
    summary     TEXT,
    created_at  TEXT NOT NULL
);

-- Registo dos agentes activos.
CREATE TABLE agents (
    slug        TEXT PRIMARY KEY,
    display_name TEXT,
    role        TEXT,
    active      INTEGER DEFAULT 1
);

-- Deliverables entregues ao utilizador (alimenta métricas de quality gate).
CREATE TABLE deliverables (
    id                        INTEGER PRIMARY KEY,
    task_id                   INTEGER REFERENCES tasks(id),
    filepath                  TEXT,
    deliverable_type          TEXT,
    quality_score             INTEGER,    -- 1..12 (estrutural + conteúdo)
    revision_rounds INTEGER,
    user_rating  INTEGER,    -- 1..10, opcional
    tags                      TEXT,       -- JSON array
    created_at                TEXT NOT NULL
);

-- Padrões aprendidos (procedural memory) — sucesso/falha por tipo de tarefa.
CREATE TABLE procedural_memory (
    id              INTEGER PRIMARY KEY,
    trigger_pattern TEXT,
    action          TEXT,
    success_count   INTEGER DEFAULT 0,
    fail_count      INTEGER DEFAULT 0,
    last_used       TEXT
);

-- Histórico de actividade append-only (auditoria e reversibilidade).
CREATE TABLE activity_history (
    id           INTEGER PRIMARY KEY,
    actor        TEXT,
    action       TEXT,
    entity_type  TEXT,
    entity_id    INTEGER,
    summary      TEXT,
    occurred_at  TEXT NOT NULL
);

-- Vista de saúde do contexto (exemplo de agregação para diagnóstico).
CREATE VIEW v_system_health AS
SELECT
    (SELECT COUNT(*) FROM tasks WHERE status = 'open')        AS open_tasks,
    (SELECT COUNT(*) FROM agents WHERE active = 1)            AS active_agents,
    (SELECT COUNT(*) FROM deliverables)                       AS total_deliverables,
    (SELECT ROUND(AVG(quality_score), 2) FROM deliverables)   AS avg_quality_score;
