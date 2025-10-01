import json
from datetime import datetime
from core.AIAdapter import AIAdapter
from models import Question, FollowUpQuestion, Answer, QuestionWithFollowUps, ExamSession, QuestionScore, CorrectionReport


def exam_gen():
    """Generate an interactive exam with 5 questions and follow-ups"""
    client = AIAdapter(model="gemini-2.5-flash")

    # Get exam topic from user
    print("=== Exam Generator ===\n")
    exam_topic = input("Enter the exam topic: ").strip()

    # Generate 2 main questions
    print(f"\n\nGenerating 2 questions about '{exam_topic}'...\n")

    response = client.generate_structured_content(
        user_prompt=f"Genera exactamente 2 preguntas de examen sobre: {exam_topic}",
        system_prompt="Eres un generador de exámenes. Genera 2 preguntas claras y bien estructuradas sobre el tema dado. Todas las preguntas deben estar en español.",
        response_schema=list[Question],
    )

    # Parse the generated questions
    questions_data = json.loads(response.text)
    main_questions = [Question(**q) for q in questions_data]

    # Initialize exam session
    exam_session = ExamSession(
        exam_topic=exam_topic,
        timestamp=datetime.now().isoformat(),
        questions=[]
    )

    # Process each main question
    for i, question in enumerate(main_questions, 1):
        print(f"\n{'='*60}")
        print(f"Question {i}/{len(main_questions)}")
        print(f"{'='*60}")
        print(f"\n{question.question_text}\n")

        # Get user's answer to main question
        main_answer_text = input("Your answer: ").strip()
        main_answer = Answer(
            question_text=question.question_text,
            answer_text=main_answer_text
        )

        # Generate 3 follow-up questions based on the answer
        print("\nGenerating follow-up questions...\n")

        followup_response = client.generate_structured_content(
            user_prompt=f"Basándote en esta pregunta: '{question.question_text}' y la respuesta del usuario: '{main_answer_text}', genera exactamente 3 preguntas de seguimiento etiquetadas como opciones 'a', 'b' y 'c'.",
            system_prompt="Eres un asistente de exámenes. Genera 3 preguntas de seguimiento relacionadas que exploren diferentes aspectos de la pregunta principal y la respuesta del usuario. Cada pregunta debe estar etiquetada con las opciones 'a', 'b' o 'c'. Todas las preguntas deben estar en español.",
            response_schema=list[FollowUpQuestion],
        )

        followups_data = json.loads(followup_response.text)
        follow_up_questions = [FollowUpQuestion(**fq) for fq in followups_data]

        # Ask each follow-up question
        follow_up_answers = []
        for followup in follow_up_questions:
            print(f"{followup.option}) {followup.question_text}\n")
            followup_answer_text = input("Your answer: ").strip()
            follow_up_answers.append(Answer(
                question_text=followup.question_text,
                answer_text=followup_answer_text
            ))
            print()

        # Store question with all follow-ups
        question_with_followups = QuestionWithFollowUps(
            main_question=question,
            main_answer=main_answer,
            follow_up_questions=follow_up_questions,
            follow_up_answers=follow_up_answers
        )
        exam_session.questions.append(question_with_followups)

    # Save exam session to JSON file
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exam_session_{timestamp_str}.json"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(exam_session.model_dump_json(indent=2))

    print(f"\n{'='*60}")
    print(f"Exam completed!")
    print(f"Session saved to: {filename}")
    print(f"{'='*60}\n")

    # === AUTO-CORRECTION PHASE ===
    print("\n" + "="*60)
    print("Starting automatic correction...")
    print("="*60 + "\n")

    # Load rubrics
    with open("exam_rubrics.json", "r", encoding="utf-8") as f:
        rubrics = json.load(f)

    rubrics_text = json.dumps(rubrics, indent=2, ensure_ascii=False)

    # Score all answers
    all_scores = []

    for i, q_with_followups in enumerate(exam_session.questions, 1):
        print(f"Scoring question {i}...")

        # Score main answer
        main_score_response = client.generate_structured_content(
            user_prompt=f"Pregunta: {q_with_followups.main_question.question_text}\nRespuesta del estudiante: {q_with_followups.main_answer.answer_text}",
            system_prompt=f"Eres un corrector de exámenes. Evalúa la siguiente respuesta según estas rúbricas:\n\n{rubrics_text}\n\nDebes proporcionar una puntuación de 0 a 10 y una justificación clara en español.",
            response_schema=QuestionScore,
        )

        main_score = QuestionScore(**json.loads(main_score_response.text))
        all_scores.append(main_score)

        # Score follow-up answers
        for followup_answer in q_with_followups.follow_up_answers:
            followup_score_response = client.generate_structured_content(
                user_prompt=f"Pregunta: {followup_answer.question_text}\nRespuesta del estudiante: {followup_answer.answer_text}",
                system_prompt=f"Eres un corrector de exámenes. Evalúa la siguiente respuesta según estas rúbricas:\n\n{rubrics_text}\n\nDebes proporcionar una puntuación de 0 a 10 y una justificación clara en español.",
                response_schema=QuestionScore,
            )

            followup_score = QuestionScore(**json.loads(followup_score_response.text))
            all_scores.append(followup_score)

    # Calculate deterministic average
    total_score = sum(score.score for score in all_scores)
    final_average = total_score / len(all_scores)

    # Create correction report
    correction_report = CorrectionReport(
        exam_session_file=filename,
        exam_topic=exam_topic,
        scores=all_scores,
        final_average=final_average,
        timestamp=datetime.now().isoformat()
    )

    # Save correction report
    correction_filename = f"exam_correction_{timestamp_str}.json"
    with open(correction_filename, "w", encoding="utf-8") as f:
        f.write(correction_report.model_dump_json(indent=2))

    # Display results
    print(f"\n{'='*60}")
    print("CORRECTION COMPLETED!")
    print(f"{'='*60}")
    print(f"Total answers evaluated: {len(all_scores)}")
    print(f"Final average score: {final_average:.2f}/10")
    print(f"Correction report saved to: {correction_filename}")
    print(f"{'='*60}\n")