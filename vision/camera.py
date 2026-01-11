import cv2
from collections import Counter
from .detector import DocumentDetector
from .processor import QuizProcessor
from .config import Config


class CameraVision:
    def __init__(self, camera_index):
        self.detector = DocumentDetector()
        self.processor = QuizProcessor()
        self.id_history = []
        self.ans_history = []
        self.camera_index = camera_index
        self.calib_data = {"A": [], "B": [], "C": [], "D": []}
        self.calib_counter = 0

    def get_frame_data(self):
        """ Reads a frame, analyzes it and returns student_id, answers if successful read. """
        cap = cv2.VideoCapture(self.camera_index)
        
        while True:
            ret, frame = cap.read()
            if not ret or cv2.waitKey(1) & 0xFF == ord('q'): 
                break

            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            warped, doc_cnt = self.detector.get_stable_warped(frame)
            
            if doc_cnt is not None:
                cv2.drawContours(frame, [doc_cnt], -1, (0, 255, 0), 2)

            if warped is not None:
                zones = self.processor.extract_zones(warped)
                student_id = self.processor.ocr_student_code(zones["student_code"])
                current_ans = self.processor.process_answers(zones["answers"])
                
                self._update_history(student_id, current_ans)
                
                final_id, stable_answers = self._get_consensus()
                
                if final_id not in ["Analyse...", "Lecture..."] and stable_answers is not None:
                    cap.release()
                    cv2.destroyAllWindows()
                    return final_id, stable_answers

            cv2.imshow("VeloxQuiz", frame)
            
        cap.release()
        cv2.destroyAllWindows()
        return None, None

    def _get_consensus(self):
        """ Calculates the most stable student ID and answers from history."""
        final_id = "Analyse..."
        if self.id_history:
            final_id, count = Counter(self.id_history).most_common(1)[0]
            if count < 3: 
                final_id = "Lecture..."

        if len(self.ans_history) < Config.HISTORY_SIZE:
            return final_id, None

        stable_answers = []
        for q_idx in range(10):
            votes = [frame[q_idx] for frame in self.ans_history if frame[q_idx] is not None]
            if votes:
                most_common, freq = Counter(votes).most_common(1)[0]
                stable_answers.append(most_common if freq >= Config.CONSENSUS_FREQ else "?")
            else:
                stable_answers.append(".")
        
        return final_id, stable_answers

    def _update_history(self, sid, answers):
        if sid: self.id_history.append(sid)
        self.ans_history.append(answers)
        if len(self.id_history) > Config.HISTORY_SIZE: self.id_history.pop(0)
        if len(self.ans_history) > Config.HISTORY_SIZE: self.ans_history.pop(0)
        
    def reset_session(self):
        self.id_history = []
        self.ans_history = []