class SensorType:
    """
    Клас для представлення типу сенсора (наприклад, температура, CO2, шум).
    """

    def __init__(self, name: str, unit: str):
        self.name = name
        self.unit = unit
