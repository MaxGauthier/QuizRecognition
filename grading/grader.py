from typing import List, Dict, Any
from src.core.aiwrapper import Quiz

class QuizGrader:
    def __init__(self, quiz_obj: Quiz):
        self.quiz = quiz_obj
        
        self.correct_answers = {
            q.question_id: q.correct_answer 
            for q in self.quiz.questions
        }

    def grade(self, student_answers: List[str]) -> Dict[str, Any]:
        """Compare quiz answer and correct answers. Manages uncertain detection. """
        score = 0
        details = []

        for index, student_ans in enumerate(student_answers):
            q_id = index + 1
            correct = self.correct_answers.get(q_id)

            if student_ans == "?":
                status = "NOT_GRADED"
                is_correct = False
            else:
                is_correct = (student_ans == correct)
                if is_correct:
                    score += 1
                status = "OK" if is_correct else "ERR"

            details.append({
                "id": q_id,
                "student": student_ans,
                "correct": correct,
                "status": status
            })

        total = len(self.correct_answers)
        needs_review = len([d for d in details if d["status"] == "NOT_GRADED"])

        return {
            "score": score,
            "total": total,
            "percentage": (score / total * 100) if total > 0 else 0,
            "needs_review": needs_review,
            "details": details
        }