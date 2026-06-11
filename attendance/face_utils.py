import os
import cv2
import numpy as np
from django.conf import settings

HAAR_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)


def detect_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    return faces, gray


def load_students():
    from .models import Student
    students = Student.objects.exclude(face_image='')
    faces = []
    labels = []
    label_map = {}
    for idx, student in enumerate(students):
        if not student.face_image:
            continue
        path = os.path.join(settings.MEDIA_ROOT, student.face_image.name)
        if not os.path.exists(path):
            continue
        img = cv2.imread(path)
        if img is None:
            continue
        faces_detected, gray = detect_face(img)
        if len(faces_detected) > 0:
            (x, y, w, h) = faces_detected[0]
            face_roi = gray[y:y + h, x:x + w]
            face_roi = cv2.resize(face_roi, (200, 200))
            faces.append(face_roi)
            labels.append(idx)
            label_map[idx] = student
    return faces, labels, label_map


def get_face_roi_from_image(image):
    faces_detected, gray = detect_face(image)
    if len(faces_detected) == 0:
        return None, gray
    (x, y, w, h) = faces_detected[0]
    face_roi = gray[y:y + h, x:x + w]
    face_roi = cv2.resize(face_roi, (200, 200))
    return face_roi, gray