# Эндпоинты REST-API для детекции СИЗ

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from app.models.yolo_detector import YoloDetector
from app.utils.image_processing import allowed_file

api_bp = Blueprint('api', __name__)

detector = YoloDetector()


@api_bp.route('/detect', methods=['POST'])
def detect_ppe():
    """Эндпоинт для детекции СИЗ на загруженном изображении."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: jpg, jpeg, png'}), 400

    # Сохранение файла
    filename = secure_filename(file.filename)
    upload_path = os.path.join(api_bp.root_path, '..', 'static', 'uploads', filename)
    file.save(upload_path)

    try:
        # Детекция
        results, _ = detector.detect(upload_path)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500