# System Design

## Agent Roles

### 1. Study Material Analyst
- **Responsibility**: Reads all files in the `materials/` directory and produces a structured knowledge summary
- **Input**: Course material files (`.txt`, `.md`, `.pdf`)
- **Output**: A knowledge summary (key topics, concepts, facts) cached on the session
- **Tools**: `DirectoryReadTool`, `FileReadTool`

### 2. Question Generator
- **Responsibility**: Generates assessment questions grounded in the study material
- **Input**: Material summary, difficulty level, session history
- **Output**: A clear, targeted question based on the source material

### 3. Response Evaluator
- **Responsibility**: Evaluates student answers against the study material
- **Input**: Material summary, the question asked, and the student's response
- **Output**: Score (0-10), feedback, concepts demonstrated/missing

### 4. Difficulty Adjuster
- **Responsibility**: Adjusts difficulty based on student performance
- **Input**: Recent scores and session state
- **Output**: New difficulty level (1-5)

## Communication Flow

```
[Materials] → [Study Agent] → summary ─┐
                                        ├→ [Question Generator] → question → [Student]
[Student] → answer → [Evaluator] ──────┘        ↑
                         ↓                       │
                       score → [Difficulty Adjuster] → level
```

## Session Lifecycle

1. Session starts — Study Agent reads and summarises all materials
2. Material summary is cached on the session
3. Question Generator creates first question based on the material
4. Student provides answer
5. Evaluator scores the answer against the source material
6. After 2+ questions, Difficulty Adjuster recalibrates
7. Loop until max questions reached
8. Final summary presented

If `materials/` is empty, agents fall back to general LLM knowledge.

## Data Models

All inter-agent communication uses Pydantic models for type safety and validation.
See `src/models/` for schema definitions.

Key fields:
- `AssessmentSession.material_summary` — cached study output, passed to question and evaluation tasks
- `Settings.materials_dir` — configurable path to the materials folder (`ASSESS_MATERIALS_DIR`)
