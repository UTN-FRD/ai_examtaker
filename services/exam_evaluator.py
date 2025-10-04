"""
Exam Evaluator Service
Handles the automatic correction and evaluation of exam sessions
"""

import json
from datetime import datetime
from typing import List

from core.AIAdapter import AIAdapter
from models import ExamSession, QuestionScore, CorrectionReport


class ExamEvaluator:
    """Service responsible for evaluating exam answers and generating correction reports"""
    
    def __init__(self):
        self.client = AIAdapter(model="gemini-2.5-flash")
        self._rubrics = self._load_rubrics()
    
    def _load_rubrics(self) -> dict:
        """Load evaluation rubrics from JSON file"""
        with open("exam_rubrics.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _get_rubrics_text(self) -> str:
        """Get rubrics formatted as text for prompts"""
        return json.dumps(self._rubrics, indent=2, ensure_ascii=False)
    
    def evaluate_answer(self, question_text: str, answer_text: str) -> QuestionScore:
        """
        Evaluate a single answer using AI and rubrics
        
        Args:
            question_text: The question that was answered
            answer_text: The student's answer
            
        Returns:
            QuestionScore object with score and justification
        """
        rubrics_text = self._get_rubrics_text()
        
        score_response = self.client.generate_structured_content(
            user_prompt=f"Pregunta: {question_text}\nRespuesta del estudiante: {answer_text}",
            system_prompt=f"Eres un corrector de exámenes. Evalúa la siguiente respuesta según estas rúbricas:\n\n{rubrics_text}\n\nDebes proporcionar una puntuación de 0 a 10 y una justificación clara en español.",
            response_schema=QuestionScore,
        )
        
        return QuestionScore(**json.loads(score_response.text))
    
    def evaluate_exam_session(self, exam_session: ExamSession) -> List[QuestionScore]:
        """
        Evaluate all answers in an exam session
        
        Args:
            exam_session: The exam session to evaluate
            
        Returns:
            List of QuestionScore objects for all answers
        """
        all_scores = []
        
        print("\n" + "="*60)
        print("Starting automatic correction...")
        print("="*60 + "\n")
        
        for i, q_with_followups in enumerate(exam_session.questions, 1):
            print(f"Scoring question {i}...")
            
            # Score main answer
            main_score = self.evaluate_answer(
                q_with_followups.main_question.question_text,
                q_with_followups.main_answer.answer_text
            )
            all_scores.append(main_score)
            
            # Score follow-up answers
            for followup_answer in q_with_followups.follow_up_answers:
                followup_score = self.evaluate_answer(
                    followup_answer.question_text,
                    followup_answer.answer_text
                )
                all_scores.append(followup_score)
        
        return all_scores
    
    def calculate_final_score(self, scores: List[QuestionScore]) -> float:
        """
        Calculate the final average score from all individual scores
        
        Args:
            scores: List of QuestionScore objects
            
        Returns:
            Final average score (0-10)
        """
        if not scores:
            return 0.0
        
        total_score = sum(score.score for score in scores)
        return total_score / len(scores)
    
    def create_correction_report(
        self, 
        exam_session: ExamSession, 
        scores: List[QuestionScore],
        exam_session_filename: str
    ) -> CorrectionReport:
        """
        Create a complete correction report
        
        Args:
            exam_session: The original exam session
            scores: List of all scored answers
            exam_session_filename: Name of the session file
            
        Returns:
            CorrectionReport object
        """
        final_average = self.calculate_final_score(scores)
        
        return CorrectionReport(
            exam_session_file=exam_session_filename,
            exam_topic=exam_session.exam_topic,
            scores=scores,
            final_average=final_average,
            timestamp=datetime.now().isoformat()
        )
    
    def save_correction_report(self, correction_report: CorrectionReport) -> str:
        """
        Save correction report to JSON file
        
        Args:
            correction_report: The correction report to save
            
        Returns:
            Filename of the saved report
        """
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exam_correction_{timestamp_str}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(correction_report.model_dump_json(indent=2))
        
        return filename
    
    def display_correction_results(self, correction_report: CorrectionReport, correction_filename: str):
        """
        Display correction results to the user
        
        Args:
            correction_report: The correction report to display
            correction_filename: Name of the correction file
        """
        print(f"\n{'='*60}")
        print("CORRECTION COMPLETED!")
        print(f"{'='*60}")
        print(f"Total answers evaluated: {len(correction_report.scores)}")
        print(f"Final average score: {correction_report.final_average:.2f}/10")
        print(f"Correction report saved to: {correction_filename}")
        print(f"{'='*60}\n")
    
    def correct_and_report(self, exam_session: ExamSession, exam_session_filename: str) -> CorrectionReport:
        """
        Complete correction workflow: evaluate answers and create report
        
        Args:
            exam_session: The exam session to correct
            exam_session_filename: Name of the session file
            
        Returns:
            Complete CorrectionReport object
        """
        # Evaluate all answers
        scores = self.evaluate_exam_session(exam_session)
        
        # Create correction report
        correction_report = self.create_correction_report(exam_session, scores, exam_session_filename)
        
        # Save report and display results
        correction_filename = self.save_correction_report(correction_report)
        self.display_correction_results(correction_report, correction_filename)
        
        return correction_report
