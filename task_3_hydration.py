import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

df = pd.read_excel("data.xlsx")

# Ключові стовпці
col_los = "Кількість ліжко-днів"
col_dehydration = "Dehydration"
col_temperature = "Temperature"

df[col_los] = pd.to_numeric(df[col_los], errors="coerce")
df[col_temperature] = pd.to_numeric(df[col_temperature], errors="coerce")

# Очищення Dehydration
df[col_dehydration] = df[col_dehydration].fillna("No dehydration")
df[col_dehydration] = df[col_dehydration].astype(str).str.strip()
df[col_dehydration] = df[col_dehydration].replace(
    {"": "No dehydration", "nan": "No dehydration"}
)
valid_dehydration = ["No dehydration", "Mild dehydration", "Severe dehydration"]
df[col_dehydration] = df[col_dehydration].apply(
    lambda x: x if x in valid_dehydration else "No dehydration"
)

df[col_dehydration] = df[col_dehydration].replace(
    {
        "No dehydration": "Відсутність дегідратації",
        "Mild dehydration": "Легка",
        "Severe dehydration": "Важка",
    }
)

df_cleaned = df.dropna(subset=[col_los, col_temperature])

# === Розрахунок лінійної регресії ===
dehydration_order = (
    df_cleaned.groupby(col_dehydration)[col_los].mean().sort_values().index
)
sns.boxplot(
    data=df_cleaned,
    x=col_dehydration,
    y=col_los,
    order=dehydration_order,
)

plt.title("Залежність ліжко-днів від ступеня дегідратації")
plt.xlabel("Ступінь дегідратації")
plt.ylabel("Кількість ліжко-днів")

plt.tight_layout()
filename = "3_Дегідратація_vs_Ліжко_дні.png"
plt.savefig(filename)
print(f"Збережено графік: '{filename}'")

print("\n--- Завершення аналізу Завдання 3 (Дегідратація) ---")
