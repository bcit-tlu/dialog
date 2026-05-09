from pydantic import BaseModel, Field

from models.question import Question
from models.response import StudentResponse, Evaluation


class QuestionRecord(BaseModel):
    """A record of a single question-answer-evaluation cycle."""

    question: Question
    response: StudentResponse | None = None
    evaluation: Evaluation | None = None


class AssessmentSession(BaseModel):
    """Tracks the state of an entire assessment session."""

    subject: str = Field(description="The subject domain being assessed")
    current_difficulty: int = Field(default=3, ge=1, le=5)
    history: list[QuestionRecord] = Field(default_factory=list)
    is_complete: bool = False
    material_summary: str = Field(default="", description="Cached study material summary")

    @property
    def questions_asked(self) -> int:
        return len(self.history)

    @property
    def average_score(self) -> float:
        scores = [
            r.evaluation.score
            for r in self.history
            if r.evaluation is not None
        ]
        return sum(scores) / len(scores) if scores else 0.0
