import cv2
import numpy as np

try:
    import mediapipe as mp
except ImportError:
    mp = None


class TFLiteHandDetector:
    """改造成基于MediaPipe Hands的检测器，保留旧接口方便游戏控制器复用"""

    def __init__(self, max_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.5):
        self.max_hands = max_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.detector = None
        self.is_loaded = False

        if mp is None:
            print("未检测到mediapipe，无法启用高级手势检测器")
            return

        self._initialize_detector()

    def _initialize_detector(self):
        """构建MediaPipe Hands实例"""
        try:
            self.detector = mp.solutions.hands.Hands(
                static_image_mode=False,
                model_complexity=1,
                max_num_hands=self.max_hands,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence,
            )
            self.is_loaded = True
            print("MediaPipe手势检测器初始化成功")
        except Exception as e:
            print(f"初始化MediaPipe手势检测器失败: {e}")
            self.detector = None
            self.is_loaded = False

    def detect_landmarks(self, img):
        """检测手部关键点"""
        if not self.is_loaded or self.detector is None:
            return [], img

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb_img)

        img_height, img_width, _ = img.shape
        detected_hands = []

        if results.multi_hand_landmarks:
            handedness_list = results.multi_handedness or []
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                lmList = []
                for landmark in hand_landmarks.landmark:
                    x = int(landmark.x * img_width)
                    y = int(landmark.y * img_height)
                    z = landmark.z
                    lmList.append((x, y, z))

                hand_type = "Right"
                if idx < len(handedness_list):
                    label = handedness_list[idx].classification[0].label
                    hand_type = "Left" if label.lower() == "left" else "Right"

                hand_info = {
                    "lmList": lmList,
                    "bbox": self.calculate_bbox(lmList, img_width, img_height),
                    "type": hand_type,
                }
                detected_hands.append(hand_info)

        if detected_hands:
            self.draw_landmarks(img, detected_hands)

        return detected_hands, img

    def calculate_bbox(self, lmList, img_width, img_height):
        """计算手部边界框"""
        if not lmList:
            return (0, 0, 0, 0)

        xs = [np.clip(lm[0], 0, img_width) for lm in lmList]
        ys = [np.clip(lm[1], 0, img_height) for lm in lmList]

        x_min = int(min(xs))
        y_min = int(min(ys))
        x_max = int(max(xs))
        y_max = int(max(ys))

        width = x_max - x_min
        height = y_max - y_min

        return (x_min, y_min, width, height)

    def draw_landmarks(self, img, hands):
        """绘制手部关键点和连接线"""
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
        ]

        for hand in hands:
            lmList = hand["lmList"]
            for connection in connections:
                start_idx, end_idx = connection
                if start_idx < len(lmList) and end_idx < len(lmList):
                    start_point = lmList[start_idx]
                    end_point = lmList[end_idx]
                    cv2.line(img, (start_point[0], start_point[1]), (end_point[0], end_point[1]), (0, 255, 0), 2)

            for i, lm in enumerate(lmList):
                color = (0, 0, 255) if i == 8 else (0, 255, 0)
                cv2.circle(img, (lm[0], lm[1]), 5, color, cv2.FILLED)

    def findHands(self, img, draw=True, flipType=False):
        """兼容cvzone.HandDetector的接口"""
        if flipType:
            img = cv2.flip(img, 1)

        hands, processed_img = self.detect_landmarks(img)

        if not draw:
            processed_img = img

        cvzone_hands = []
        for hand in hands:
            cvzone_hands.append(
                {
                    "lmList": hand["lmList"],
                    "bbox": hand["bbox"],
                    "type": hand["type"],
                }
            )

        return cvzone_hands, processed_img
