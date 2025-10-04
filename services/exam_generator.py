"""
Exam Generator Service
Handles the generation of exam questions and interactive session management
"""

import json
from datetime import datetime
from typing import List

from core.AIAdapter import AIAdapter
from models import (
    Question, 
    FollowUpQuestion, 
    Answer, 
    QuestionWithFollowUps, 
    ExamSession
)


class ExamGenerator:
    """Service responsible for generating exam questions and managing question sessions"""
    
    def __init__(self):
        self.client = AIAdapter(model="gemini-2.5-flash")
    
    def generate_main_questions(self, exam_topic: str, num_questions: int = 2) -> List[Question]:
        """
        Generate main exam questions based on topic
        
        Args:
            exam_topic: The topic for the exam
            num_questions: Number of questions to generate (default: 2)
            
        Returns:
            List of Question objects
        """
        print(f"\n\nGenerating {num_questions} questions about '{exam_topic}'...\n")
        
        response = self.client.generate_structured_content(
            user_prompt=f"Genera exactamente {num_questions} preguntas de examen sobre: {exam_topic}",
            system_prompt="Eres un generador de exámenes. Genera preguntas claras y bien estructuradas sobre el tema dado. Todas las preguntas deben estar en español.",
            response_schema=list[Question],
        )
        
        questions_data = json.loads(response.text)
        return [Question(**q) for q in questions_data]
    
    def generate_follow_up_questions(self, main_question: Question, user_answer: str) -> List[FollowUpQuestion]:
        """
        Generate follow-up questions based on main question and user's answer
        
        Args:
            main_question: The original question
            user_answer: User's answer to the main question
            
        Returns:
            List of FollowUpQuestion objects
        """
        print("\nGenerating follow-up questions...\n")
        
        followup_response = self.client.generate_structured_content(
            user_prompt=f"Basándote en esta pregunta: '{main_question.question_text}' y la respuesta del usuario: '{user_answer}', genera exactamente 3 preguntas de seguimiento etiquetadas como opciones 'a', 'b' y 'c'.",
            system_prompt="Eres un asistente de exámenes. Genera 3 preguntas de seguimiento relacionadas que exploren diferentes aspectos de la pregunta principal y la respuesta del usuario. Cada pregunta debe estar etiquetada con las opciones 'a', 'b' o 'c'. Todas las preguntas deben estar en español.",
            response_schema=list[FollowUpQuestion],
        )
        
        followups_data = json.loads(followup_response.text)
        return [FollowUpQuestion(**fq) for fq in followups_data]
    
    def collect_user_answer(self, question_text: str) -> str:
        """
        Collect user answer for a question
        
        Args:
            question_text: The question being answered
            
        Returns:
            User's answer as string
        """
        return input("Your answer: ").strip()
    
    def collect_answers_for_follow_ups(self, follow_up_questions: List[FollowUpQuestion]) -> List[Answer]:
        """
        Collect answers for all follow-up questions
        
        Args:
            follow_up_questions: List of follow-up questions to answer
            
        Returns:
            List of Answer objects
        """
        follow_up_answers = []
        
        for followup in follow_up_questions:
            print(f"{followup.option}) {followup.question_text}\n")
            followup_answer_text = input("Your answer: ").strip()
            follow_up_answers.append(Answer(
                question_text=followup.question_text,
                answer_text=followup_answer_text
            ))
            print()
        
        return follow_up_answers
    
    def process_question_session(self, question: Question) -> QuestionWithFollowUps:
        """
        Process a complete question session (main question + follow-ups + answers)
        
        Args:
            question: The main question to process
            
        Returns:
            QuestionWithFollowUps object with all data
        """
        print(f"\n{'='*60}")
        print(f"Question {question.question_number}")
        print(f"{'='*60}")
        print(f"\n{question.question_text}\n")
        
        # Get user's answer to main question
        main_answer_text = self.collect_user_answer(question.question_text)
        main_answer = Answer(
            question_text=question.question_text,
            answer_text=main_answer_text
        )
        
        # Generate and collect follow-up questions and answers
        follow_up_questions = self.generate_follow_up_questions(question, main_answer_text)
        follow_up_answers = self.collect_answers_for_follow_ups(follow_up_questions)
        
        # Combine everything into QuestionWithFollowUps
        return QuestionWithFollowUps(
            main_question=question,
            main_answer=main_answer,
            follow_up_questions=follow_up_questions,
            follow_up_answers=follow_up_answers
        )
    
    def create_exam_session(self, exam_topic: str) -> ExamSession:
        """
        Create a complete exam session with questions and user interaction
        
        Args:
            exam_topic: The topic for the exam
            
        Returns:
            Complete ExamSession object
        """
        # Generate main questions
        main_questions = self.generate_main_questions(exam_topic)
        
        # Initialize exam session
        exam_session = ExamSession(
            exam_topic=exam_topic,
            timestamp=datetime.now().isoformat(),
            questions=[]
        )
        
        # Process each question session
        for i, question in enumerate(main_questions, 1):
            question.question_number = i  # Ensure numbering is correct
            question_session = self.process_question_session(question)
            exam_session.questions.append(question_session)
        
        return exam_session
    
    def save_exam_session(self, exam_session: ExamSession) -> str:
        """
        Save exam session to JSON file
        
        Args:
            exam_session: The exam session to save
            
        Returns:
            Filename of the saved file
        """
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exam_session_{timestamp_str}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(exam_session.model_dump_json(indent=2))
        
        print(f"\n{'='*60}")
        print(f"Exam completed!")
        print(f"Session saved to: {filename}")
        print(f"{'='*60}\n")
        
        return filename
