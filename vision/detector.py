import cv2
import numpy as np
from .utils import perspective_transform
from .config import Config

class DocumentDetector:
    def __init__(self):
        self.stable_counter = 0
        self.last_center = None

    def get_stable_warped(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edged = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 75, 200)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        doc_cnt = self._find_rectangular_contour(contours)
        
        if doc_cnt is not None:
            if self._is_stable(doc_cnt):
                self.stable_counter += 1
            else:
                self.stable_counter = 0
            
            if self.stable_counter >= Config.STABILITY_THRESHOLD:
                return perspective_transform(frame, doc_cnt), doc_cnt
        else:
            self.stable_counter = 0
            
        return None, doc_cnt

    def _is_stable(self, contour):
        m = cv2.moments(contour)

        if m["m00"] == 0: 
            return False
        
        curr_center = (int(m["m10"]/m["m00"]), int(m["m01"]/m["m00"]))
        
        if self.last_center is None:
            self.last_center = curr_center
            return True
        
        dist = np.linalg.norm(np.array(curr_center) - np.array(self.last_center))
        self.last_center = curr_center

        return dist < Config.MOVEMENT_TOLERANCE

    def _find_rectangular_contour(self, contours):
        for c in sorted(contours, key=cv2.contourArea, reverse=True):
            if cv2.contourArea(c) < Config.MIN_DOC_AREA: break
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4: 
                return approx
            
        return None