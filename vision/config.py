class Config:
    # Stability thresholds
    STABILITY_THRESHOLD = 8
    MOVEMENT_TOLERANCE = 20
    HISTORY_SIZE = 10
    CONSENSUS_FREQ = 7

    # Image analysis parameters
    MIN_DOC_AREA = 25000

    # ROI Ratios
    ROI_ID_Y = (0.05, 0.1)
    ROI_ID_X = (0.80, 0.97)
    ROI_ANSWERS_Y = (0.10, 0.95)
    ROI_ANSWERS_X = (0.75, 0.95)
    REC_SIZE = 0.3

    # Detection processor.py thresholds
    MIN_BUBBLE_SCORE = 180
    MIN_GAP = 40
    STRONG_MARK_THRESHOLD = 300
    NO_MARK_THRESHOLD = 60
    GAP_BIAS = {
        'A': {'B': -20, 'C': -5,  'D': -25},
        'B': {'A': 20, 'C': 15, 'D': -5},
        'C': {'A': 5,  'B': -15, 'D': -20},
        'D': {'A': 25, 'B': 5,  'C': 20}
    }
    DETECTION_OFFSET = 30
    OPTION_AVGS = {
        'A': 85,
        'B': 105,
        'C': 90,
        'D': 120
    }
