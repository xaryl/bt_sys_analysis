import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

df = pd.read_excel("data.xlsx")

col_los = "Кількість ліжко-днів"
col_age_years = "Вік, років"
col_age_m = "Age1 (m)"
col_age_d = "Age2 (d)"

df[col_los] = pd.to_numeric(df[col_los], errors="coerce")
df[col_age_years] = pd.to_numeric(df[col_age_years], errors="coerce")
df[col_age_m] = pd.to_numeric(df[col_age_m], errors="coerce")
df[col_age_d] = pd.to_numeric(df[col_age_d], errors="coerce")

age_years = df[col_age_years].fillna(0)
age_m = df[col_age_m].fillna(0)
age_d = df[col_age_d].fillna(0)
df["Total_Age_Months"] = (age_years * 12) + age_m + (age_d / 30.4375)

df_cleaned = df.dropna(subset=[col_los, "Total_Age_Months"])

# === Розрахунок лінійної регресії ===
print("Розрахунок лінійної регресії...")
slope, intercept, r_value, p_value, std_err = stats.linregress(
    df_cleaned["Total_Age_Months"], df_cleaned[col_los]
)
print(f"  Нахил (slope): {slope:.4f}")
print(f"  Перетин (intercept): {intercept:.4f}")
print(f"  Коефіцієнт кореляції (r): {r_value:.4f}")
print(f"  Коефіцієнт детермінації (R-squared): {r_value**2:.4f}")
print(f"  P-value: {p_value:.4f}")

# === Побудова графіка ===
plt.figure(figsize=(10, 6))

sns.scatterplot(data=df_cleaned, x="Total_Age_Months", y=col_los, alpha=0.6)

sns.regplot(
    data=df_cleaned, x="Total_Age_Months", y=col_los, scatter=False, color="red"
)

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

plt.title("Залежність ліжко-днів від віку пацієнта")
plt.xlabel("Вік (місяці)")
plt.ylabel("Кількість ліжко-днів")

plt.tight_layout()
filename = "3_Вік_vs_Ліжко_дні.png"
plt.savefig(filename)
print(f"Збережено графік: '{filename}'")

print("\n--- Завершення аналізу Завдання 3 (Вік) ---")
