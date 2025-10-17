import cv2
import numpy as np
import time

# Load Haar cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

video = cv2.VideoCapture(0)

# Resizable window
cv2.namedWindow("Face and Eye Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Face and Eye Detection", 640, 480)

# Timer variables
timer_running = False
timer_start_time = 0
total_no_face_time = 0  # Cumulative time

# Helper function: Eye gaze direction
def get_eye_direction(eye_roi_gray):
    blur = cv2.GaussianBlur(eye_roi_gray, (7, 7), 0)
    _, threshold = cv2.threshold(blur, 30, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        (x, y, w, h) = cv2.boundingRect(largest_contour)
        cx = x + w // 2
        eye_width = eye_roi_gray.shape[1]

        if cx < eye_width / 3:
            return "Looking Left"
        elif cx > 2 * eye_width / 3:
            return "Looking Right"
        else:
            return "Looking Center"
    return "Gaze Undetected"

while True:
    ret, frame = video.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    face_detected = len(faces) > 0

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 255, 50), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]

        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 2)
            eye_gray = roi_gray[ey:ey + eh, ex:ex + ew]
            gaze_direction = get_eye_direction(eye_gray)
            cv2.putText(roi_color, gaze_direction, (ex, ey - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # ⏱ Timer logic — cumulative
    if not face_detected:
        if not timer_running:
            timer_start_time = time.time()
            timer_running = True
        else:
            # Add time difference to total
            elapsed = time.time() - timer_start_time
            total_no_face_time += elapsed
            timer_start_time = time.time()  # restart timer for next loop
    else:
        timer_running = False

    # 🔴 Red or 🟢 Green Button
    button_x, button_y = 20, 20
    button_w, button_h = 80, 40
    if face_detected:
        cv2.rectangle(frame, (button_x, button_y), (button_x + button_w, button_y + button_h), (0, 255, 0), -1)
        cv2.putText(frame, "OK", (button_x + 15, button_y + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    else:
        cv2.rectangle(frame, (button_x, button_y), (button_x + button_w, button_y + button_h), (0, 0, 255), -1)
        cv2.putText(frame, "NO", (button_x + 15, button_y + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # 🕒 Display cumulative timer
    cv2.putText(frame, f"Total No Face Time: {int(total_no_face_time)} sec", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    resized_frame = cv2.resize(frame, (640, 480))
    cv2.imshow("Face and Eye Detection", resized_frame)

    if cv2.waitKey(1) & 0xFF == ord('e'):
        break

video.release()
cv2.destroyAllWindows()
