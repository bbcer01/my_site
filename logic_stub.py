from schemas import TTResponse

def evaluate_tt_measure(tnved_code: str, product_name: str) -> TTResponse:
    # Заглушка: возвращает фиксированный результат
    return TTResponse(
        measure="Повышение ставки таможенной пошлины до уровня 35-50%",
        reason="Заглушка: доля импорта из недружественных стран >30%."
    )