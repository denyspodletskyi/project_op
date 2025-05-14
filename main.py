from datetime import datetime
import json
import os
from typing import Dict, List, Any, Optional
import uuid


class SensorType:
    """Клас, що представляє тип датчика та містить його характеристики"""

    def __init__(self, name: str, unit: str, min_value: float, max_value: float):
        """
        Ініціалізація типу датчика

        Args:
            name: Назва типу датчика 
            unit: Одиниця вимірювання
            min_value: Мінімальне допустиме значення
            max_value: Максимальне допустиме значення
        """
        self.name = name
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value

    def format_reading(self, value: float) -> str:
        """
        Форматування показника датчика

        Args:
            value: Значення показника

        Returns:
            Форматований рядок з показником та одиницею вимірювання
        """
        return f"{value:.2f} {self.unit}"

    def validate_reading(self, value: float) -> bool:
        """
        Перевірка, чи потрапляє значення в допустимий діапазон

        Args:
            value: Значення для перевірки

        Returns:
            True, якщо значення допустиме, False - якщо ні
        """
        return self.min_value <= value <= self.max_value

    def __str__(self) -> str:
        return f"{self.name} (вимірюється в {self.unit})"


class Sensor:
    """Клас, що представляє IoT-датчик для збору екологічних даних"""

    def __init__(self, sensor_id: str, location: Dict[str, float], sensor_type: SensorType):
        """
        Ініціалізація датчика

        Args:
            sensor_id: Унікальний ідентифікатор датчика
            location: Місце розташування (широта, довгота)
            sensor_type: Тип датчика
        """
        self.sensor_id = sensor_id
        self.location = location
        self.sensor_type = sensor_type
        self.readings = []

    def add_reading(self, value: float, timestamp: Optional[datetime] = None) -> bool:
        """
        Додавання нового показника з датчика

        Args:
            value: Значення показника
            timestamp: Час зняття показника (якщо не вказано, використовується поточний час)

        Returns:
            True, якщо показник валідний і був доданий, False - якщо показник невалідний
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Перевірка валідності показника
        if not self.sensor_type.validate_reading(value):
            print(f"Помилка: показник {value} виходить за межі допустимих значень для датчика {self.sensor_id}")
            return False

        reading = {
            "value": value,
            "timestamp": timestamp.isoformat(),
            "formatted_value": self.sensor_type.format_reading(value)
        }
        self.readings.append(reading)
        return True

    def get_latest_reading(self) -> Dict[str, Any]:
        """
        Отримання останнього показника датчика

        Returns:
            Останній показник або порожній словник, якщо показників немає
        """
        if not self.readings:
            return {}
        return self.readings[-1]

    def get_average_reading(self) -> float:
        """
        Розрахунок середнього значення показників

        Returns:
            Середнє значення показників або 0, якщо показників немає
        """
        if not self.readings:
            return 0
        return sum(reading["value"] for reading in self.readings) / len(self.readings)

    def to_dict(self) -> Dict[str, Any]:
        """
        Перетворення даних датчика в словник

        Returns:
            Словник з даними датчика
        """
        return {
            "sensor_id": self.sensor_id,
            "location": self.location,
            "sensor_type": self.sensor_type.name,
            "readings_count": len(self.readings),
            "latest_reading": self.get_latest_reading(),
            "average_reading": self.get_average_reading()
        }

    def __str__(self) -> str:
        latest = self.get_latest_reading()
        latest_str = latest.get("formatted_value", "немає даних") if latest else "немає даних"
        return f"Датчик {self.sensor_id} ({self.sensor_type.name}), локація: {self.location}, останній показник: {latest_str}"


class DataCollector:
    """Клас, що відповідає за збір та зберігання інформації з датчиків"""

    def __init__(self, name: str):
        """
        Ініціалізація збирача даних

        Args:
            name: Назва системи збору даних
        """
        self.name = name
        self.sensors = {}  # Словник датчиків: sensor_id -> Sensor
        self.sensor_types = {}  # Словник типів датчиків: name -> SensorType
        self.reports = []  # Список звітів

    def register_sensor_type(self, name: str, unit: str, min_value: float, max_value: float) -> SensorType:
        """
        Реєстрація нового типу датчика

        Args:
            name: Назва типу датчика
            unit: Одиниця вимірювання
            min_value: Мінімальне допустиме значення
            max_value: Максимальне допустиме значення

        Returns:
            Створений тип датчика
        """
        sensor_type = SensorType(name, unit, min_value, max_value)
        self.sensor_types[name] = sensor_type
        return sensor_type

    def create_sensor(self, location: Dict[str, float], sensor_type_name: str) -> Optional[Sensor]:
        """
        Створення нового датчика

        Args:
            location: Місце розташування (широта, довгота)
            sensor_type_name: Назва типу датчика

        Returns:
            Створений датчик або None, якщо тип датчика не існує
        """
        if sensor_type_name not in self.sensor_types:
            print(f"Помилка: тип датчика '{sensor_type_name}' не зареєстровано")
            return None

        sensor_id = str(uuid.uuid4())[:8]  # Генерація унікального ID
        sensor = Sensor(sensor_id, location, self.sensor_types[sensor_type_name])
        self.sensors[sensor_id] = sensor
        return sensor

    def add_reading(self, sensor_id: str, value: float) -> bool:
        """
        Додавання показника для датчика

        Args:
            sensor_id: ID датчика
            value: Значення показника

        Returns:
            True, якщо показник додано успішно, False - якщо датчик не існує або значення невалідне
        """
        if sensor_id not in self.sensors:
            print(f"Помилка: датчик з ID '{sensor_id}' не існує")
            return False

        return self.sensors[sensor_id].add_reading(value)

    def generate_report(self, title: str, sensor_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Генерація звіту на основі показників датчиків

        Args:
            title: Назва звіту
            sensor_ids: Список ID датчиків для включення в звіт (якщо None, використовуються всі датчики)

        Returns:
            Звіт у вигляді словника
        """
        if sensor_ids is None:
            sensor_ids = list(self.sensors.keys())

        sensors_data = []
        for sensor_id in sensor_ids:
            if sensor_id in self.sensors:
                sensors_data.append(self.sensors[sensor_id].to_dict())

        report = {
            "title": title,
            "generated_at": datetime.now().isoformat(),
            "sensors_count": len(sensors_data),
            "sensors": sensors_data
        }

        self.reports.append(report)
        return report

    def validate_report(self, report_index: int) -> bool:
        """
        Перевірка звіту на відповідність зібраним даним

        Args:
            report_index: Індекс звіту в списку звітів

        Returns:
            True, якщо звіт відповідає даним датчиків, False - якщо ні
        """
        if report_index < 0 or report_index >= len(self.reports):
            print(f"Помилка: звіт з індексом {report_index} не існує")
            return False

        report = self.reports[report_index]
        for sensor_data in report["sensors"]:
            sensor_id = sensor_data["sensor_id"]

            if sensor_id not in self.sensors:
                print(f"Помилка: у звіті є датчик {sensor_id}, який не існує в системі")
                return False

            sensor = self.sensors[sensor_id]

            # Перевірка кількості показників
            if sensor_data["readings_count"] != len(sensor.readings):
                print(f"Помилка: невідповідність кількості показників для датчика {sensor_id}")
                return False

            # Перевірка середнього значення (з урахуванням невеликої похибки через округлення)
            if abs(sensor_data["average_reading"] - sensor.get_average_reading()) > 0.01:
                print(f"Помилка: невідповідність середнього значення для датчика {sensor_id}")
                return False

        return True

    def save_report_to_file(self, report_index: int, filename: str) -> bool:
        """
        Збереження звіту в JSON-файл

        Args:
            report_index: Індекс звіту в списку звітів
            filename: Ім'я файлу для збереження

        Returns:
            True, якщо звіт успішно збережено, False - якщо виникла помилка
        """
        if report_index < 0 or report_index >= len(self.reports):
            print(f"Помилка: звіт з індексом {report_index} не існує")
            return False

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.reports[report_index], f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Помилка при збереженні звіту: {e}")
            return False

    def load_data(self, filename: str) -> bool:
        """
        Завантаження даних з JSON-файлу

        Args:
            filename: Ім'я файлу для завантаження

        Returns:
            True, якщо дані успішно завантажено, False - якщо виникла помилка
        """
        if not os.path.exists(filename):
            print(f"Помилка: файл {filename} не існує")
            return False

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Завантаження типів датчиків
            for sensor_type_data in data.get("sensor_types", []):
                self.register_sensor_type(
                    sensor_type_data["name"],
                    sensor_type_data["unit"],
                    sensor_type_data["min_value"],
                    sensor_type_data["max_value"]
                )

            # Завантаження датчиків
            for sensor_data in data.get("sensors", []):
                sensor = self.create_sensor(
                    sensor_data["location"],
                    sensor_data["sensor_type"]
                )

                # Завантаження показників
                for reading in sensor_data.get("readings", []):
                    timestamp = datetime.fromisoformat(reading["timestamp"])
                    sensor.add_reading(reading["value"], timestamp)

            return True
        except Exception as e:
            print(f"Помилка при завантаженні даних: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Отримання статистики по всій системі

        Returns:
            Словник зі статистикою
        """
        sensor_types_count = {name: 0 for name in self.sensor_types.keys()}
        readings_total = 0

        for sensor in self.sensors.values():
            sensor_types_count[sensor.sensor_type.name] += 1
            readings_total += len(sensor.readings)

        return {
            "total_sensors": len(self.sensors),
            "total_readings": readings_total,
            "sensors_by_type": sensor_types_count,
            "reports_generated": len(self.reports)
        }


# Приклад використання системи
def demo_system():
    # Створення системи збору даних
    collector = DataCollector("Міська система моніторингу екології")

    # Реєстрація типів датчиків
    collector.register_sensor_type("Якість повітря PM2.5", "мкг/м³", 0, 500)
    collector.register_sensor_type("Якість повітря PM10", "мкг/м³", 0, 1000)
    collector.register_sensor_type("Температура", "°C", -50, 60)
    collector.register_sensor_type("Вологість", "%", 0, 100)
    collector.register_sensor_type("Рівень шуму", "дБ", 0, 150)
    collector.register_sensor_type("Якість води pH", "pH", 0, 14)

    # Створення датчиків в різних локаціях міста
    sensor1 = collector.create_sensor({"lat": 50.4501, "lon": 30.5234}, "Якість повітря PM2.5")  # Київ, центр
    sensor2 = collector.create_sensor({"lat": 50.4601, "lon": 30.5334}, "Якість повітря PM10")  # Київ, інша локація
    sensor3 = collector.create_sensor({"lat": 50.4501, "lon": 30.5234}, "Температура")  # Київ, центр
    sensor4 = collector.create_sensor({"lat": 50.4481, "lon": 30.5203}, "Вологість")  # Київ, парк
    sensor5 = collector.create_sensor({"lat": 50.4401, "lon": 30.5184}, "Рівень шуму")  # Київ, вулиця
    sensor6 = collector.create_sensor({"lat": 50.4511, "lon": 30.5244}, "Якість води pH")  # Київ, річка

    # Імітація додавання показників з датчиків
    collector.add_reading(sensor1.sensor_id, 15.2)  # PM2.5
    collector.add_reading(sensor1.sensor_id, 18.7)
    collector.add_reading(sensor1.sensor_id, 21.3)

    collector.add_reading(sensor2.sensor_id, 45.6)  # PM10
    collector.add_reading(sensor2.sensor_id, 52.1)

    collector.add_reading(sensor3.sensor_id, 24.5)  # Температура
    collector.add_reading(sensor3.sensor_id, 25.2)
    collector.add_reading(sensor3.sensor_id, 26.0)

    collector.add_reading(sensor4.sensor_id, 65.3)  # Вологість
    collector.add_reading(sensor4.sensor_id, 67.8)

    collector.add_reading(sensor5.sensor_id, 72.6)  # Рівень шуму
    collector.add_reading(sensor5.sensor_id, 85.3)
    collector.add_reading(sensor5.sensor_id, 78.9)

    collector.add_reading(sensor6.sensor_id, 7.2)  # pH води
    collector.add_reading(sensor6.sensor_id, 7.4)

    # Спроба додати невалідне значення
    print("\nСпроба додати невалідне значення:")
    result = collector.add_reading(sensor3.sensor_id, 70.0)  # Температура вище максимальної
    print(f"Результат додавання невалідного значення: {'успішно' if result else 'відхилено'}")

    # Генерація звіту для всіх датчиків
    print("\nГенерація загального звіту:")
    report = collector.generate_report("Щоденний звіт про екологічну ситуацію в місті")
    print(f"Звіт створено: {report['title']}, {report['sensors_count']} датчиків")

    # Генерація звіту тільки для датчиків якості повітря
    air_sensors = [sensor1.sensor_id, sensor2.sensor_id]
    air_report = collector.generate_report("Звіт про якість повітря", air_sensors)
    print(f"Звіт про повітря створено: {air_report['title']}, {air_report['sensors_count']} датчиків")

    # Валідація звітів
    print("\nВалідація звітів:")
    is_valid_report1 = collector.validate_report(0)
    print(f"Загальний звіт валідний: {is_valid_report1}")

    is_valid_report2 = collector.validate_report(1)
    print(f"Звіт про повітря валідний: {is_valid_report2}")

    # Отримання статистики
    print("\nСтатистика системи:")
    stats = collector.get_statistics()
    print(f"Всього датчиків: {stats['total_sensors']}")
    print(f"Всього показників: {stats['total_readings']}")
    print(f"Розподіл датчиків за типами: {stats['sensors_by_type']}")
    print(f"Згенеровано звітів: {stats['reports_generated']}")

    # Збереження звіту у файл
    collector.save_report_to_file(0, "eco_report.json")
    print("\nЗагальний звіт збережено у файл 'eco_report.json'")


if __name__ == "__main__":
    demo_system()