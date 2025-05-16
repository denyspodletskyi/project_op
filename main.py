import json
from datetime import datetime
from sensor_type import SensorType
from sensor import Sensor
from data_collector import DataCollector
from recommendation import get_recommendation
from decorators import log_action


@log_action
def save_to_json(entry):
    """
    Зберігає отримані дані у файл JSON.
    """
    filename = "eco_log.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(entry)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    """
        Тута вказується тип сенсора
    """
    temperature = SensorType("Температура", "°C")
    co2 = SensorType("CO2", "ppm")
    pm25 = SensorType("PM2.5", "µg/m³")
    humidity = SensorType("Вологість", "%")

    available_types = {
        "Температура": temperature,
        "CO2": co2,
        "PM2.5": pm25,
        "Вологість": humidity
    }

    sensors = [
        Sensor("S1", temperature, "Центр"),
        Sensor("S2", co2, "Промзона"),
        Sensor("S3", pm25, "Житловий район"),
        Sensor("S4", humidity, "Парк")
    ]

    print("🌍 Вітаю у системі моніторингу екологічних показників 🌱")

    while True:
        print("\n📌 Який екологічний показник вас цікавить?")
        print("(оберіть: Температура, CO2, PM2.5, Вологість)")
        print("або введіть 'Дякую тобі, на цьому все' — для виходу")

        choice = input("👉 Ваш вибір: ").strip()

        if choice == "Дякую тобі, на цьому все":
            print("\n💚 Дякую! Бережіть себе і довкілля!")
            break

        if choice not in available_types:
            print("⚠️ Невідомий тип. Спробуйте ще раз.")
            continue

        selected_type = available_types[choice]
        collector = DataCollector()

        for sensor in sensors:
            if sensor.sensor_type.name == selected_type.name:
                collector.collect(sensor)

        print(f"\n📊 [Звіт по показнику: {selected_type.name}]")
        for entry in collector.data:
            recommendation = get_recommendation(entry["type"], entry["value"])
            print(
                f"📍 {entry['location']} – {entry['type']}: {entry['value']:.2f} {entry['unit']}\n"
                f"💡 Рекомендація: {recommendation}\n"
            )
            """
               Ось тут записується дата та рекомендація, та збереження даних в eco_log.json 
            """

            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry["recommendation"] = recommendation

            save_to_json(entry)


if __name__ == "__main__":
    main()
