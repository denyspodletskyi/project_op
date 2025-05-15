from validator import validate_value


class Sensor:
    """
    Тут базовий клас сенсора IoT
    """

    def __init__(self, sensor_id: str, sensor_type, location: str):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location

    def read_data(self):
        """
        Тут реалізований метод,який має повертати згенероване значення та потім застосовувати його
        """
        import random
        value = random.uniform(0, 100)
        return validate_value(value, self.sensor_type.name)
