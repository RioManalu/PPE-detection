import torch
import numpy as np
import cv2
import time
from playsound import playsound


### Ini koding IoTnya mas #####################
from paho.mqtt import client as mqtt
broker = "broker.emqx.io"
topic = "Arsuya/test"
client = mqtt.Client()
client.connect(broker)

# Langsung liat method score_frame dan perhatikan code client.publish()

##########################################


class ObjectDetection: 
    """
    Class implements Yolo5 model to make inferences on a youtube video using OpenCV.
    """
    
    def __init__(self):
        """
        Initializes the class with youtube url and output file.
        :param url: Has to be as youtube URL,on which prediction is made.
        :param out_file: A valid output file name.
        """
        self.model = self.load_model()
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("\n\nDevice Used:",self.device)


    def load_model(self):
        """
        Loads Yolo5 model from pytorch hub.
        :return: Trained Pytorch model.

        load from path trained pt file that you stored in your local
        """
        # model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        # model = torch.hub.load('/home/riohanson/.cache/torch/hub/ultralytics_yolov5_master', 'custom', source='local', path='yolov5/runs/train/exp51/weights/last.pt', force_reload=True)
        # model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/runs/train/exp51/weights/last.pt', force_reload=True)
        model = torch.hub.load('C:/Users/arsuy/MachineLearning/Yolov5-training/yolov5', 'custom', source='local', path='yolov5/runs/train/exp78/weights/best.pt', force_reload=True)
        return model


    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)


        if len(results.pred[0]):
            print(results)
            print(results.names)
            print(results.pred)
            # print(results.pred[0][-1][-1])
            # print(type(results.pred[0][-1][-1]))
            for i in range(len(results.pred[0])):
                print(results.pred[0][i][-1])
                if results.pred[0][i][-1] == 1 or results.pred[0][i][-1] == 2 or results.pred[0][i][-1] == 3:
                    # playsound('sound/audio4.mp3')

                    # Di bawah ini berfungsi utk mengirimkan pesan '1' ke arduino
                    client.publish(topic, "1")
                    print("-------------------------- warning detected ------------------------------")
                else:

                    # Di bawah ini berfungsi utk mengirimkan pesan '0' ke arduino
                    client.publish(topic, "0")
            print("=======================================")
        else: 
            client.publish(topic, "0")
        # print(results)
        # print(results.pred)
        # print(len(results.pred[0]))
        


        # if results.pred("nvest"):
        #     print("=============== ke-detect nvest =========")
        # elif results.pred("shoes") or results.pred("shoess"):
        #     print("=============== ke detect shoes =========")
        # if results.__contains__("nhelmet") or results.__contains__("nvest") or results.__contains__("nshoes"):
        #     print("oke")
        
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        print(labels, cord)
        return labels, cord


    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]


    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            if labels[i] == 1 or labels[i] == 2 or labels[i] == 3:
                print(labels[i], type(labels[i]))
                row = cord[i]
                if row[4] >= 0.4:
                    x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                    bgr = (0,0,255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                    cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)
            elif labels[i] == 0 or labels[i] == 4 or labels[i] == 5:
                row = cord[i]
                if row[4] >= 0.4:
                    x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                    bgr = (0,255,0)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                    cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)
        return frame


    def __call__(self):
        """
        This function is called when class is executed, it runs the loop to read the video frame by frame,
        and write the output into a new file.
        :return: void
        """
        cap = cv2.VideoCapture(1)

        while cap.isOpened():
            
            start_time = time.perf_counter()
            ret, frame = cap.read()
            if not ret:
                client.publish(topic, "0")
                break
            results = self.score_frame(frame)
            frame = self.plot_boxes(results, frame)
            end_time = time.perf_counter()
            fps = 1 / np.round(end_time - start_time, 3)
            cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
            # cv2.imshow("img", frame)

            rtrn,buffer = cv2.imencode('.jpg',frame)
            frm = buffer.tobytes()
            yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frm + b'\r\n')

            if cv2.waitKey(1) & 0xFF == ord('q'):
                client.publish(topic, "0")
                break
        else:
            client.publish(topic, "0")


# Create a new object and execute.
# detection = ObjectDetection()
# detection()