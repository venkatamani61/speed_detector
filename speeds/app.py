import os
from flask import Flask, render_template, request, redirect, url_for, Response
from detect import detect_and_track

UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

video_source = None  # Global variable to store video source (path or camera index)

@app.route('/')
def index():
    return render_template('index.html', show_video=False)

@app.route('/upload', methods=['POST'])
def upload_video():
    global video_source

    input_mode = request.form.get('input_mode')

    if input_mode == 'camera':
        video_source = 0  # Use webcam
        return render_template('index.html', show_video=True)

    elif input_mode == 'file':
        file = request.files.get('video_file')
        if file and file.filename:
            filename = file.filename
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            video_source = video_path
            return render_template('index.html', show_video=True)

    return redirect(url_for('index'))

@app.route('/video_feed')
def video_feed():
    global video_source
    return Response(detect_and_track(video_source),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=8080)
