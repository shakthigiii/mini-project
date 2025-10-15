import cv2

# Load pre-trained Haar Cascade models for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Start webcam
video = cv2.VideoCapture(0)

# Create a window and set it to fullscreen
cv2.namedWindow("Face and Eye Detection", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Face and Eye Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = video.read()
    if not ret:
        break

    # Convert frame to grayscale for better detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Get frame dimensions
    height, width, _ = frame.shape

    # Loop through detected faces
    for (x, y, w, h) in faces:
        # Draw rectangle around face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 255, 50), 2)

        # Define region of interest (face area)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]

        # Detect eyes within the face region
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 2)

    # Warning and messages
    if len(faces) > 1:
        text = " Multiple Faces Detected!"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1.2, 3)[0]
        text_x = (width - text_size[0]) // 2
        text_y = (height + text_size[1]) // 2

        # Red warning text at center
        cv2.putText(frame, text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1.2, (0, 0, 255), 3)
    elif len(faces) == 1:
        cv2.putText(frame, "  Face Detected", (30, 50),
                    cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 0.6, (0, 255, 0), 1)
    else:
        cv2.putText(frame, "No Face Detected", (30, 50),
                    cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 0.6, (0, 0, 255), 1)

    # Display frame
    cv2.imshow("Face and Eye Detection", frame)

    # Quit with 'e'
    if cv2.waitKey(1) & 0xFF == ord('e'):
        break

video.release()
cv2.destroyAllWindows()
