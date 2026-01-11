import cv2
import numpy as np
import easyocr
import re
from .config import Config

class QuizProcessor:
    def __init__(self, languages=['en']):
        self.reader = easyocr.Reader(languages, gpu=False)

    def extract_zones(self, warped_image):
        h, w = warped_image.shape[:2]
        y1, y2 = Config.ROI_ID_Y
        x1, x2 = Config.ROI_ID_X
        
        ay1, ay2 = Config.ROI_ANSWERS_Y
        ax1, ax2 = Config.ROI_ANSWERS_X

        return {
            "student_code": warped_image[int(h*y1):int(h*y2), int(w*x1):int(w*x2)],
            "answers": warped_image[int(h*ay1):int(h*ay2), int(w*ax1):int(w*ax2)]
        }
    
    def ocr_student_code(self, roi, body_len=8, key_len=2):
        if roi is None or roi.size == 0: 
            return None
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_LANCZOS4)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 15)

        results = self.reader.readtext(thresh, detail=0, allowlist='0123456789-')
        if not results: 
            return None

        raw_text = "".join(results).replace(" ", "")
        match = re.search(rf'(\d{{{body_len}}}-?\d{{{key_len}}})', raw_text)
        return match.group(1) if match else None
    
    def process_answers(self, answers_zone, nb_questions=10, nb_options=4):
        gray = cv2.cvtColor(answers_zone, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        h, w = thresh.shape
        row_h = h / nb_questions
        col_w = w / nb_options
        choices = []

        for i in range(nb_questions):
            scores = []
            for j in range(nb_options):
                y1 = int(i * row_h + row_h * Config.REC_SIZE)
                y2 = int((i+1) * row_h - row_h * Config.REC_SIZE)
                x1 = int(j * col_w + col_w * Config.REC_SIZE)
                x2 = int((j+1) * col_w - col_w * Config.REC_SIZE)
                
                score = cv2.countNonZero(thresh[y1:y2, x1:x2])
                scores.append(score)       

            # DEBUG PRINT
            #print(f"Ligne {i+1:02d} | A:{scores[0]:3d} B:{scores[1]:3d} C:{scores[2]:3d} D:{scores[3]:3d}")
            choices.append(self._decide_choice(scores))

        return choices
    
    def _decide_choice(self, scores):
        options = ["A", "B", "C", "D"]
        
        candidates_idx = []
        for i, score in enumerate(scores):
            opt = options[i]
            threshold = Config.OPTION_AVGS[opt] + Config.DETECTION_OFFSET
            if score > threshold:
                candidates_idx.append(i)

        if not candidates_idx:
            return None

        strong_marks = [i for i in candidates_idx if scores[i] > Config.STRONG_MARK_THRESHOLD]
        if len(strong_marks) > 1:
            return None

        sorted_indices = np.argsort(scores)[::-1]
        best_idx = sorted_indices[0]
        second_idx = sorted_indices[1]
        
        if best_idx not in candidates_idx:
            return None

        actual_gap = scores[best_idx] - scores[second_idx]
        required_gap = Config.MIN_GAP + Config.GAP_BIAS[options[best_idx]][options[second_idx]]

        if actual_gap > required_gap:
            return options[best_idx]
        
        return None
    
    def get_only_scores(self, answers_zone, nb_questions=10, nb_options=4):
        gray = cv2.cvtColor(answers_zone, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        h, w = thresh.shape
        row_h, col_w = h / nb_questions, w / nb_options
        
        all_rows_scores = []
        for i in range(nb_questions):
            row = []
            for j in range(nb_options):
                y1 = int(i * row_h + row_h * Config.REC_SIZE)
                y2 = int((i + 1) * row_h - row_h * Config.REC_SIZE)
                x1 = int(j * col_w + col_w * Config.REC_SIZE)
                x2 = int((j + 1) * col_w - col_w * Config.REC_SIZE)
                row.append(cv2.countNonZero(thresh[y1:y2, x1:x2]))
            all_rows_scores.append(row)
        return all_rows_scores