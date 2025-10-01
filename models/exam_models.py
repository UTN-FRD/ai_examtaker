from pydantic import BaseModel, Field


class Question(BaseModel):
    """Main exam question"""
    question_text: str = Field(description="The question text")
    question_number: int = Field(description="Question number in the exam")


class FollowUpQuestion(BaseModel):
    """Follow-up question (a, b, or c)"""
    question_text: str = Field(description="The follow-up question text")
    option: str = Field(description="Option identifier: a, b, or c")


class Answer(BaseModel):
    """User answer to a question"""
    question_text: str = Field(description="The question that was answered")
    answer_text: str = Field(description="The user's answer")


class QuestionWithFollowUps(BaseModel):
    """Main question with its follow-ups and answers"""
    main_question: Question
    main_answer: Answer | None = None
    follow_up_questions: list[FollowUpQuestion] = Field(default_factory=list)
    follow_up_answers: list[Answer] = Field(default_factory=list)


class ExamSession(BaseModel):
    """Complete exam session data"""
    exam_topic: str = Field(description="The topic of the exam")
    questions: list[QuestionWithFollowUps] = Field(default_factory=list)
    timestamp: str = Field(description="Session timestamp")


class QuestionScore(BaseModel):
    """Score for a single answer"""
    question_text: str = Field(description="The question that was scored")
    answer_text: str = Field(description="The answer that was scored")
    score: float = Field(description="Score from 0 to 10", ge=0, le=10)
    justification: str = Field(description="Justification for the score")


class CorrectionReport(BaseModel):
    """Complete correction report for an exam session"""
    exam_session_file: str = Field(description="Original exam session filename")
    exam_topic: str = Field(description="Topic of the exam")
    scores: list[QuestionScore] = Field(default_factory=list)
    final_average: float = Field(description="Final average score (0-10)", ge=0, le=10)
    timestamp: str = Field(description="Correction timestamp")