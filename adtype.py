import pandas as pd
import re

# Набір для зберігання унікальних, очищених назв
all_drugs_set = set()

# Завантажуємо ваш файл
df = pd.read_excel("data.xlsx")

# Обираємо колонку 'Adtype', видаляємо пусті значення (NaN)
# і конвертуємо все в рядки
adtype_series = df["Adtype"].dropna().astype(str)

print("Починаю обробку стовпця 'Adtype'...")

# Ітеруємо по кожному запису в колонці
for entry in adtype_series:
    # Розділяємо запис, який може містити декілька ліків.
    # Роздільники: кома, новий рядок (\n), або специфічний код Excel _x000D_
    raw_names = re.split(r"[,\n]|_x000D_", entry)

    # Ітеруємо по кожній "сирій" назві
    for name in raw_names:
        # 1. Очищуємо від сміття: лапки, зірочки і т.д.
        cleaned_name = name.strip(" \"'*")

        # 2. Переводимо в нижній регістр
        cleaned_name = cleaned_name.lower()

        # 3. Видаляємо інформацію про дозування (напр. "3x1 sachet", "4x400mg", "10mg/kg")
        # \b - межа слова
        # [\d./x]+ - одна або більше цифр, крапок, слешів, 'x'
        # [a-zA-Z\s/()]* - будь-які літери, пробіли, слеші, дужки, що йдуть після
        cleaned_name = re.sub(r"\b[\d./x]+[a-zA-Z\s/()]*\b", "", cleaned_name)

        # 4. Видаляємо будь-які залишкові окремі цифри
        cleaned_name = re.sub(r"\b\d+\b", "", cleaned_name)

        # 5. Видаляємо спеціальні символи, залишаючи літери та пробіли
        cleaned_name = re.sub(r"[^a-zA-Z\s]", " ", cleaned_name)

        # 6. Прибираємо зайві пробіли
        cleaned_name = re.sub(r"\s+", " ", cleaned_name).strip()

        # 7. Додаємо до набору, якщо назва має сенс (довша за 2 літери)
        if len(cleaned_name) > 2:
            all_drugs_set.add(cleaned_name)

# Виводимо результат
if all_drugs_set:
    print("\n--- Знайдені унікальні назви ліків ---")
    # Конвертуємо набір в список, сортуємо і виводимо
    for drug in sorted(list(all_drugs_set)):
        print(drug)
