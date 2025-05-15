class DataCollector:
    """
    Тут клас для збору та обробки даних з сенсорів
    """

    def __init__(self):
        self.data = []

    def collect(self, sensor):
        try:
            value = sensor.read_data()
            self.data.append({
                "sensor_id": sensor.sensor_id,
                "type": sensor.sensor_type.name,
                "value": value,
                "unit": sensor.sensor_type.unit,
                "location": sensor.location
            })
        except ValueError as e:
            print(f"[!] Помилка зчитування: {e}")

    def report(self):
        for entry in self.data:
            print(f"{entry['location']} – {entry['type']}: {entry['value']} {entry['unit']}")
