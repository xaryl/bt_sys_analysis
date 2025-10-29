import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

df = pd.read_excel("data.xlsx")

col_los = "Кількість ліжко-днів"
col_temperature = "Temperature"

df[col_los] = pd.to_numeric(df[col_los], errors="coerce")
df[col_temperature] = pd.to_numeric(df[col_temperature], errors="coerce")

df_cleaned = df.dropna(subset=[col_los, col_temperature])

# === Розрахунок лінійної регресії ===
print("Розрахунок лінійної регресії...")
slope, intercept, r_value, p_value, std_err = stats.linregress(
    df_cleaned[col_temperature], df_cleaned[col_los]
)
print(f"  Нахил (slope): {slope:.4f}")
print(f"  Перетин (intercept): {intercept:.4f}")
print(f"  Коефіцієнт кореляції (r): {r_value:.4f}")
print(f"  Коефіцієнт детермінації (R-squared): {r_value**2:.4f}")
print(f"  P-value: {p_value:.4f}")

# === Побудова графіка ===
plt.figure(figsize=(10, 6))

sns.scatterplot(data=df_cleaned, x=col_temperature, y=col_los, alpha=0.6)

sns.regplot(data=df_cleaned, x=col_temperature, y=col_los, scatter=False, color="red")

equation = f"y = {slope:.3f}x + {intercept:.2f}\n$R^2 = {r_value**2:.3f}$"

plt.text(
    0.05,
    0.95,
    equation,
    transform=plt.gca().transAxes,
    fontsize=12,
    verticalalignment="top",
    bbox=dict(boxstyle="round,pad=0.5", fc="wheat", alpha=0.5),
)

plt.title("Залежність ліжко-днів від температури")
plt.xlabel("Температура (°C)")
plt.ylabel("Кількість ліжко-днів")

plt.tight_layout()
filename = "3_Температура_vs_Ліжко_дні.png"
plt.savefig(filename)
print(f"Збережено графік: '{filename}'")

print("\n--- Завершення аналізу Завдання 3 (Температура) ---")
