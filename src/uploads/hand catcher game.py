import cv2
import mediapipe as mp
import numpy as np
import random
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

## game variables
balls = []
ball_radius = 15
fall_speed = 10
spawn_interval = 0.5
last_spawn_time = time.time()
score = 0

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)  # mirror
    h, w, c = frame.shape

    # Convert BGR -> RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # spawn balls
    if time.time() - last_spawn_time > spawn_interval:
        balls.append({"x": random.randint(ball_radius, w - ball_radius), "y": 0})
        last_spawn_time = time.time()

    # move balls
    for ball in balls:
        ball["y"] += fall_speed

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # hand points
            thumb_base = (int(hand_landmarks.landmark[2].x * w), int(hand_landmarks.landmark[2].y * h))
            thumb_tip = (int(hand_landmarks.landmark[4].x * w), int(hand_landmarks.landmark[4].y * h))
            index_base = (int(hand_landmarks.landmark[5].x * w), int(hand_landmarks.landmark[5].y * h))
            index_tip = (int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h))

            curve_points = np.array([thumb_tip, thumb_base, index_base, index_tip], dtype=np.int32)
            cv2.polylines(frame, [curve_points], isClosed=False, color=(0, 255, 0), thickness=2)

            # check collisions
            new_balls = []
            for ball in balls:
                inside = cv2.pointPolygonTest(curve_points, (ball["x"], ball["y"]), False)
                if inside >= 0:  # caught
                    score += 1
                    continue
                else:
                    new_balls.append(ball)
            balls = new_balls

    # draw balls
    for ball in balls:
        cv2.circle(frame, (ball["x"], ball["y"]), ball_radius, (0, 0, 255), -1)

    # draw score
    cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.imshow("Catch The Balls", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
