# Утилиты для обработки изображений

import os

def allowed_file(filename):
    """Проверка допустимого типа файла."""
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS