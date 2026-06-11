import os
import cv2
import numpy as np
from datetime import date
from django.conf import settings
from .face_utils import load_students, get_face_roi_from_image


def train_recognizer():
    faces, labels, label_map = load_students()
    if len(faces) == 0:
        return None, label_map
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    return recognizer, label_map


def recognize_and_mark_attendance(captured_image_path, class_name):
    from .models import Student, AttendanceRecord

    img = cv2.imread(captured_image_path)
    if img is None:
        return {'error': 'Could not read captured image'}

    face_roi, gray = get_face_roi_from_image(img)
    if face_roi is None:
        return {'error': 'No face detected in the captured image'}

    recognizer, label_map = train_recognizer()
    if recognizer is None:
        return {'error': 'No registered students with face data found. Register students first.'}

    label, confidence = recognizer.predict(face_roi)
    today = date.today()

    if confidence < 70:
        student = label_map.get(label)
        if student and student.class_name == class_name:
            AttendanceRecord.objects.update_or_create(
                student=student,
                date=today,
                defaults={'status': AttendanceRecord.PRESENT, 'note': 'Marked via face recognition'}
            )
            return {
                'success': True,
                'student_name': f'{student.first_name} {student.last_name}',
                'student_id': student.student_id,
                'confidence': round(confidence, 2),
                'class_name': student.class_name,
            }
        elif student:
            return {
                'success': False,
                'error': f'Recognized {student.first_name} {student.last_name} but they belong to class "{student.class_name}", not "{class_name}"',
                'confidence': round(confidence, 2),
            }
        else:
            return {'success': False, 'error': 'Student not found in database', 'confidence': round(confidence, 2)}
    else:
        return {'success': False, 'error': 'Face not recognized', 'confidence': round(confidence, 2)}