# Класс для работы с моделью YOLOv8 для детекции СИЗ

from ultralytics import YOLO
import cv2
import numpy as np
import os


class YoloDetector:
    def __init__(self, person_model_path='app/models/yolov8s.pt', ppe_model_path='app/models/ppe_detector.pt'):
        """Инициализация моделей YOLO для детекции людей и СИЗ."""
        # Проверка наличия файлов моделей
        if not os.path.exists(person_model_path):
            raise FileNotFoundError(f"Модель для детекции людей не найдена: {person_model_path}")
        if not os.path.exists(ppe_model_path):
            raise FileNotFoundError(f"Модель для детекции СИЗ не найдена: {ppe_model_path}")

        print(f"Загрузка модели для людей: {person_model_path}")
        self.model_person = YOLO(person_model_path)
        print(f"Загрузка модели для СИЗ: {ppe_model_path}")
        self.model_ppe = YOLO(ppe_model_path)
        self.conf_threshold = 0.5

    def detect(self, image_path):
        """Детекция людей и СИЗ на изображении."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Не удалось загрузить изображение: {image_path}")

        results = []

        # Детекция людей
        results_person = self.model_person(image, conf=self.conf_threshold)
        persons = results_person[0].boxes

        for i, box in enumerate(persons):
            if box.cls == 0:  # Класс 0 — человек
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                person_conf = float(box.conf)
                person_crop = image[y1:y2, x1:x2]

                # Детекция СИЗ
                results_ppe = self.model_ppe(person_crop, conf=self.conf_threshold)
                ppe_detected = results_ppe[0].boxes

                has_helmet = False
                helmet_conf = 0.0
                has_workwear = False
                workwear_conf = 0.0

                for ppe_box in ppe_detected:
                    class_name = results_ppe[0].names[int(ppe_box.cls)]
                    conf = float(ppe_box.conf)
                    if class_name == 'helmet':
                        has_helmet = True
                        helmet_conf = max(helmet_conf, conf)
                    if class_name == 'workwear':
                        has_workwear = True
                        workwear_conf = max(workwear_conf, conf)

                # Сохранение результатов
                results.append({
                    'person_id': i,
                    'person_confidence': person_conf,
                    'has_helmet': has_helmet,
                    'helmet_confidence': helmet_conf,
                    'has_workwear': has_workwear,
                    'workwear_confidence': workwear_conf,
                    'bounding_box': [x1, y1, x2, y2]
                })

        return results, image

    def draw_results(self, image, results, output_path):
        """Отрисовка результатов детекции на изображении."""
        for result in results:
            x1, y1, x2, y2 = result['bounding_box']
            color = (0, 255, 0) if result['has_helmet'] and result['has_workwear'] else (0, 0, 255)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            label = f"Helmet: {result['has_helmet']}, Workwear: {result['has_workwear']}"
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imwrite(output_path, image)
        return output_path