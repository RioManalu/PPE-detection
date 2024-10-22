from flask import Flask, render_template, Response, request, redirect
import json
import deteksi


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/processUserInfo/<string:userinfo>', methods=['POST'])
def processUserInfo(userinfo):
    print(userinfo)
    userinfo=json.loads(userinfo)
    print(userinfo)
    print(type(userinfo))

    if userinfo == 'video':
        return ('/video')
    return('/')


@app.route('/video')
def video():
    detection = deteksi.ObjectDetection()
    return Response(detection(),mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__=="__main__":
    app.run(debug=True)

# capture = cv.VideoCapture(0)

# def generate_frames():
#     while True:
            
#         ## read the camera frame
#         success,frame = capture.read()
#         if not success:
#             break
#         else:
#             ret,buffer = cv.imencode('.jpg',frame)
#             frame = buffer.tobytes()

#         yield(b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')