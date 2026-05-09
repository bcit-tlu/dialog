from pathlib import Path

import streamlit as st

from crew.assessment_crew import AssessmentCrew
from models.session import AssessmentSession, QuestionRecord
from models.question import Question
from models.response import StudentResponse, Evaluation
from config.settings import settings


st.set_page_config(
    page_title="AI Assessment System",
    page_icon="🎓",
    layout="centered",
)

st.title("Multi-Agent Conversational Assessment")
st.caption(f"Subject: {settings.subject_domain} | Model: {settings.ollama_model}")


# Initialise session state
if "session" not in st.session_state:
    st.session_state.session = AssessmentSession(
        subject=settings.subject_domain,
        current_difficulty=settings.initial_difficulty,
    )
if "crew" not in st.session_state:
    st.session_state.crew = AssessmentCrew()
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "awaiting_answer" not in st.session_state:
    st.session_state.awaiting_answer = False


def display_chat():
    """Render chat history."""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def start_assessment():
    """Run the study phase then generate the first question."""
    session = st.session_state.session
    crew = st.session_state.crew

    # Study phase — run once and cache on the session
    with st.spinner("Studying materials..."):
        session.material_summary = crew.study_materials()

    with st.spinner("Generating question..."):
        question_text = crew.generate_question(
            session, material_summary=session.material_summary
        )
    st.session_state.current_question = question_text
    st.session_state.messages.append(
        {"role": "assistant", "content": question_text}
    )
    st.session_state.awaiting_answer = True


def handle_answer(answer: str):
    """Process a student's answer through evaluation and difficulty adjustment."""
    session = st.session_state.session
    crew = st.session_state.crew

    # Record the student message
    st.session_state.messages.append({"role": "user", "content": answer})

    # Evaluate the response
    with st.spinner("Evaluating your response..."):
        eval_text = crew.evaluate_response(
            st.session_state.current_question,
            answer,
            material_summary=session.material_summary,
        )

    st.session_state.messages.append(
        {"role": "assistant", "content": eval_text}
    )

    # Record in session history
    record = QuestionRecord(
        question=Question(
            content=st.session_state.current_question,
            topic=session.subject,
            difficulty=session.current_difficulty,
        ),
        response=StudentResponse(answer=answer, question_id=session.questions_asked),
        evaluation=Evaluation(
            score=5,  # TODO: parse score from eval_text
            feedback=eval_text,
        ),
    )
    session.history.append(record)

    # Adjust difficulty
    if session.questions_asked >= 2:
        with st.spinner("Adjusting difficulty..."):
            session.current_difficulty = crew.adjust_difficulty(session)

    # Check if session is complete
    if session.questions_asked >= settings.max_questions_per_session:
        session.is_complete = True
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    f"Assessment complete! You answered {session.questions_asked} questions "
                    f"with an average score of {session.average_score:.1f}/10."
                ),
            }
        )
        st.session_state.awaiting_answer = False
    else:
        # Generate next question
        with st.spinner("Generating next question..."):
            question_text = crew.generate_question(
                session, material_summary=session.material_summary
            )
        st.session_state.current_question = question_text
        st.session_state.messages.append(
            {"role": "assistant", "content": question_text}
        )


# --- UI Layout ---

# Sidebar with session info
with st.sidebar:
    st.header("Session Info")
    session = st.session_state.session
    st.metric("Questions Asked", session.questions_asked)
    st.metric("Current Difficulty", f"{session.current_difficulty}/5")
    st.metric("Average Score", f"{session.average_score:.1f}/10")

    st.divider()
    st.subheader("Materials")
    materials_path = Path(settings.materials_dir)
    if materials_path.is_dir():
        material_files = [
            f.name for f in materials_path.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]
        if material_files:
            for name in sorted(material_files):
                st.text(f"📄 {name}")
        else:
            st.caption("No materials found.")
    else:
        st.caption("Materials folder not found.")

    st.divider()
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# Main chat area
display_chat()

# Start button or answer input
if not st.session_state.messages:
    if st.button("Start Assessment", type="primary"):
        start_assessment()
        st.rerun()
elif st.session_state.awaiting_answer and not session.is_complete:
    if answer := st.chat_input("Type your answer..."):
        handle_answer(answer)
        st.rerun()
elif session.is_complete:
    st.success("Assessment session complete. Reset from the sidebar to start again.")
