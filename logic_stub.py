import sys
import os
import io
import base64

# Добавляем путь к папке src внутри First_code_TAS, которая находится внутри EAIS
sys.path.append(os.path.join(os.path.dirname(__file__), 'First_code_TAS', 'src'))

# Теперь можно импортировать модуль из First_code_TAS
try:
    from tariff_analyzer import TariffAnalysisSystem
    print("Успешно импортирован TariffAnalysisSystem из First_code_TAS")
except ImportError as e:
    print(f"Ошибка импорта TariffAnalysisSystem: {e}")
    TariffAnalysisSystem = None # На случай ошибки


def evaluate_tt_measure(tnved_code: str, product_name: str):
    """
    Вызывает реальную логику из First_code_TAS.
    Возвращает результат и метрики.
    """
    if not TariffAnalysisSystem:
        return {
            "measure": "Ошибка логического блока",
            "reason": "Не удалось импортировать TariffAnalysisSystem",
            "metrics": {},
            "charts": [] # Список изображений (base64)
        }

    try:
        # Инициализируем систему анализа
        analysis_system = TariffAnalysisSystem()

        # --- ВАЖНО: Используем create_dashboard, как описано в README ---
        # Он возвращает fig, measures_list, metrics_dict
        fig, measures_list, metrics_dict = analysis_system.create_dashboard(tnved_code)

        # Формируем строку результата из списка мер
        measure_str = "; ".join(measures_list) if measures_list else "Меры не требуются (Мера 6)"

        # --- КОДИРОВАНИЕ ГРАФИКА В BASE64 (для возврата в JSON) ---
        # Создаем байтовый поток
        img_bytes = io.BytesIO()
        # Сохраняем фигуру в поток в формате PNG
        fig.savefig(img_bytes, format='png', dpi=300, bbox_inches='tight')
        img_bytes.seek(0)
        # Кодируем в base64
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        # Формируем data URL
        chart_data_url = f"image/png;base64,{img_base64}"
        # Закрываем фигуру, чтобы освободить память
        fig.clf() # Очищаем фигуру

        # --- ВОЗВРАЩАЕМ РЕЗУЛЬТАТ ---
        return {
            "measure": measure_str,
            "reason": "Рассчитано на основе данных First_code_TAS",
            "metrics": metrics_dict,
            "charts": [chart_data_url] # Можно добавить несколько графиков, если нужно
        }

    except Exception as e:
        # Обработка ошибок
        print(f"Ошибка в логическом блоке: {e}")
        # Возвращаем ошибку или заглушку
        return {
            "measure": "Ошибка логического блока",
            "reason": str(e),
            "metrics": {},
            "charts": []
        }
