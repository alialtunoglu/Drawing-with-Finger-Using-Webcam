import cv2
import mediapipe as mp
import numpy as np

# MediaPipe el modeli
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Çizim için boş bir beyaz tuval
drawing_canvas = None
prev_x, prev_y = None, None
drawing = False

# Parmaklar açık mı kontrol et
def fingers_open(hand_landmarks):
    tip_ids = [mp_hands.HandLandmark.INDEX_FINGER_TIP,
               mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
               mp_hands.HandLandmark.RING_FINGER_TIP,
               mp_hands.HandLandmark.PINKY_TIP]
    finger_open_status = []

    for tip_id in tip_ids:
        tip = hand_landmarks.landmark[tip_id].y
        dip = hand_landmarks.landmark[tip_id - 2].y
        finger_open_status.append(tip < dip)
    
    return all(finger_open_status)

# Webcam'den görüntü akışı
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if drawing_canvas is None:
        # Beyaz bir arka plan oluştur
        drawing_canvas = 255 * np.ones_like(frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Parmak ucunun (index finger tip) koordinatlarını al
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h, w, c = frame.shape
            cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

            if fingers_open(hand_landmarks):
                if drawing:
                    if prev_x and prev_y:
                        cv2.line(drawing_canvas, (prev_x, prev_y), (cx, cy), (255, 0, 0), 5)
                    prev_x, prev_y = cx, cy
                else:
                    drawing = True
                    prev_x, prev_y = cx, cy
            else:
                drawing = False
                prev_x, prev_y = None, None
    else:
        drawing = False
        prev_x, prev_y = None, None

    # Çizim tuvalini ekranda göster
    cv2.imshow("Drawing", drawing_canvas)
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
