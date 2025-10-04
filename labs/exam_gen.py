"""
Exam Generator Coordinator
High-level orchestration of exam generation and evaluation workflow
"""

from services import ExamGenerator, ExamEvaluator


def exam_gen():
    """Generate an interactive exam with questions and automatic correction"""
    # Initialize services
    generator = ExamGenerator()
    evaluator = ExamEvaluator()
    
    # Get exam topic from user
    print("=== Exam Generator=== \n")
    exam_topic = input("Enter the exam topic: ").strip()
    
    # === GENERATION PHASE ===
    # Create complete exam session with user interaction
    exam_session = generator.create_exam_session(exam_topic)
    
    # Save exam session
    session_filename = generator.save_exam_session(exam_session)
    
    # === EVALUATION PHASE ===
    # Perform automatic correction and generate report
    correction_report = evaluator.correct_and_report(exam_session, session_filename)
    
    return correction_report