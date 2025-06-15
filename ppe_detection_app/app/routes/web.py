# Маршруты для веб-интерфейса

from flask import Blueprint, render_template, request, current_app
from werkzeug.utils import secure_filename
import os
from app.models.yolo_detector import YoloDetector
from app.utils.image_processing import allowed_file

web_bp = Blueprint('web', __name__)

detector = YoloDetector()


@web_bp.route('/', methods=['GET'])
def index():
    """Отображение главной страницы с формой."""
    return render_template('index.html')


@web_bp.route('/upload', methods=['POST'])
def upload_image():
    """Обработка загруженного изображения и отображение результатов."""
    if 'file' not in request.files:
        return render_template('index.html', error='No file provided')

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error='No file selected')

    if not allowed_file(file.filename):
        return render_template('index.html', error='Invalid file type. Allowed: jpg, jpeg, png')

    # Сохранение файла
    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)

    try:
        # Детекция и отрисовка
        results, image = detector.detect(upload_path)
        output_filename = f"output_{filename}"
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
        detector.draw_results(image, results, output_path)

        return render_template('index.html', results=results, image_url=f"uploads/{output_filename}")
    except Exception as e:
        return render_template('index.html', error=str(e))