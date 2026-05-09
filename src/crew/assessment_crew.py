from crewai import Crew, Task, Process

from agents.question_generator import create_question_generator
from agents.evaluator import create_evaluator
from agents.difficulty_adjuster import create_difficulty_adjuster
from agents.study_agent import create_study_agent
from models.session import AssessmentSession
from config.settings import settings


class AssessmentCrew:
    """Orchestrates the multi-agent assessment workflow using CrewAI."""

    def __init__(self):
        self.question_generator = create_question_generator()
        self.evaluator = create_evaluator()
        self.difficulty_adjuster = create_difficulty_adjuster()
        self.study_agent = create_study_agent()

    def study_materials(self) -> str:
        """Run the study agent to read and summarise all materials.

        Returns the structured knowledge summary as a string.
        """
        task = Task(
            description=(
                f"Read all files in the '{settings.materials_dir}' directory. "
                "Produce a structured knowledge summary that includes: "
                "key topics, core concepts, important facts, and relationships "
                "between ideas. Return ONLY the summary, nothing else."
            ),
            expected_output=(
                "A structured knowledge summary covering all key topics, "
                "concepts, and facts from the materials."
            ),
            agent=self.study_agent,
        )

        crew = Crew(
            agents=[self.study_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        return str(result)

    def generate_question(self, session: AssessmentSession, material_summary: str = "") -> str:
        """Generate a new assessment question based on current session state."""
        context_block = (
            f"\n\nStudy Material Summary:\n{material_summary}\n\n"
            "Base your question ONLY on the material above."
            if material_summary
            else ""
        )

        task = Task(
            description=(
                f"Generate a single assessment question about {session.subject} "
                f"at difficulty level {session.current_difficulty} (scale 1-5). "
                f"Questions asked so far: {session.questions_asked}. "
                f"Average score so far: {session.average_score:.1f}/10. "
                "Return ONLY the question text, nothing else."
                f"{context_block}"
            ),
            expected_output="A single clear assessment question.",
            agent=self.question_generator,
        )

        crew = Crew(
            agents=[self.question_generator],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        return str(result)

    def evaluate_response(self, question: str, answer: str, material_summary: str = "") -> str:
        """Evaluate a student's response to a question."""
        context_block = (
            f"\n\nStudy Material Summary:\n{material_summary}\n\n"
            "Evaluate the answer ONLY against the material above."
            if material_summary
            else ""
        )

        task = Task(
            description=(
                f"Evaluate the following student response.\n\n"
                f"Question: {question}\n\n"
                f"Student Answer: {answer}\n\n"
                "Provide: a score (0-10), brief feedback, and list key concepts "
                "demonstrated vs missing. Format your response clearly."
                f"{context_block}"
            ),
            expected_output=(
                "A structured evaluation with score, feedback, "
                "concepts demonstrated, and concepts missing."
            ),
            agent=self.evaluator,
        )

        crew = Crew(
            agents=[self.evaluator],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        return str(result)

    def adjust_difficulty(self, session: AssessmentSession) -> int:
        """Determine the next difficulty level based on session history."""
        history_summary = ""
        for i, record in enumerate(session.history[-3:], 1):
            score = record.evaluation.score if record.evaluation else "N/A"
            history_summary += f"Q{i}: score={score}/10\n"

        task = Task(
            description=(
                f"Current difficulty: {session.current_difficulty}/5.\n"
                f"Recent performance:\n{history_summary}\n"
                "Based on this performance, what should the next difficulty level be? "
                "Respond with ONLY a single integer from 1 to 5."
            ),
            expected_output="A single integer from 1 to 5.",
            agent=self.difficulty_adjuster,
        )

        crew = Crew(
            agents=[self.difficulty_adjuster],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        try:
            new_difficulty = int(str(result).strip())
            return max(1, min(5, new_difficulty))
        except ValueError:
            return session.current_difficulty
