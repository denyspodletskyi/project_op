import json
from datetime import datetime
from sensor_type import SensorType
from sensor import Sensor
from data_collector import DataCollector
from recommendation import get_recommendation
from decorators import log_action
from validator import verify_reports, validate_value

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
    print("🌍 Вітаю у системі моніторингу екологічних показників 🌱")

    def add_custom_sensor_type():
        print("\n➕ Створення нового типу сенсора")
        name = input("Введіть назву нового сенсора: ").strip()
        unit = input("Введіть одиницю вимірювання: ").strip()
        location = input("Вкажіть локацію встановлення сенсора: ").strip()
        min_value = float(input("Введіть мінімально допустиме значення: "))
        max_value = float(input("Введіть максимально допустиме значення: "))
        sensor_type = SensorType(name, unit)
        return sensor_type, location, min_value, max_value

    custom_sensor_type, custom_location, min_limit, max_limit = add_custom_sensor_type()
    custom_limits = {custom_sensor_type.name: (min_limit, max_limit)}

    temperature = SensorType("Температура", "°C")
    co2 = SensorType("CO2", "ppm")
    pm25 = SensorType("PM2.5", "µg/m³")
    humidity = SensorType("Вологість", "%")

    available_types = {
        "Температура": temperature,
        "CO2": co2,
        "PM2.5": pm25,
        "Вологість": humidity,
        custom_sensor_type.name: custom_sensor_type
    }

    sensors = [
        Sensor("S1", temperature, "Центр"),
        Sensor("S2", co2, "Промзона"),
        Sensor("S3", pm25, "Житловий район"),
        Sensor("S4", humidity, "Парк"),
        Sensor("S5", custom_sensor_type, custom_location)
    ]

    while True:
        print("\n📌 Який екологічний показник вас цікавить?")
        print("(оберіть: Температура, CO2, PM2.5, Вологість або", custom_sensor_type.name, ")")
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

        valid_data = []
        for entry in collector.data:
            try:
                validated_value = validate_value(entry["value"], entry["type"])
                recommendation = get_recommendation(entry["type"], validated_value)
                entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                entry["recommendation"] = recommendation
                save_to_json(entry)
                valid_data.append(entry)
            except ValueError as e:
                print(f"⚠️ {e}")

        print(f"\n📊 [Звіт по показнику: {selected_type.name}]")
        for entry in valid_data:
            print(
                f"📍 {entry['location']} – {entry['type']}: {entry['value']:.2f} {entry['unit']}\n"
                f"💡 Рекомендація: {entry['recommendation']}\n"
            )

        try:
            with open("eco_log.json", "r", encoding="utf-8") as f:
                saved_data = json.load(f)[-len(valid_data):]

            if verify_reports(valid_data, saved_data):
                print("✅ Звіт успішно перевірено: всі дані відповідають зібраним.")
            else:
                print("❌ Помилка у звіті: деякі дані не відповідають зібраним.")
        except Exception as e:
            print(f"⚠️ Не вдалося перевірити звіт: {e}")

        add_more = input("\n🔁 Бажаєте додати новий тип сенсора? (так/ні): ").strip().lower()
        if add_more == "так":
            new_sensor_type, new_location, min_val, max_val = add_custom_sensor_type()
            available_types[new_sensor_type.name] = new_sensor_type
            sensors.append(Sensor(f"S{len(sensors)+1}", new_sensor_type, new_location))
            custom_limits[new_sensor_type.name] = (min_val, max_val)

if __name__ == "__main__":
    main()