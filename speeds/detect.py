import cv2
import math

car_cascade = cv2.CascadeClassifier("models/haarcascade_car.xml")

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def detect_and_track(video_source=0):  # Flask-compatible generator
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    distance_per_pixel = 0.05

    prev_centroids = {}
    object_id = 0
    object_speeds = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 1.1, 2)
        curr_centroids = {}

        for (x, y, w, h) in cars:
            cx, cy = x + w // 2, y + h // 2
            curr_centroids[object_id] = (cx, cy)

            matched_id = None
            for pid, pcentroid in prev_centroids.items():
                if euclidean_distance((cx, cy), pcentroid) < 50:
                    matched_id = pid
                    break

            if matched_id is not None:
                distance_px = euclidean_distance((cx, cy), prev_centroids[matched_id])
                distance_m = distance_px * distance_per_pixel
                speed = (distance_m * fps) * 3.6
                object_speeds[matched_id] = round(speed, 2)
                object_id = matched_id
            else:
                object_id += 1

            speed_display = object_speeds.get(object_id, 0.0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"Speed: {speed_display} km/h", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        prev_centroids = curr_centroids.copy()

        # Encode frame to JPEG for Flask streaming
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
