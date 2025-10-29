import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import warnings
import re

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

df = pd.read_excel("data.xlsx")

col_los = "Кількість ліжко-днів"
col_adtype = "Adtype"
col_ab = "AB"

df[col_los] = pd.to_numeric(df[col_los], errors="coerce")

PROBIOTIC_KEYS = [
    "probiotik",
    "probiotil",
    "dialac",
    "lacto b",
    "bio",
]
ANTIBIOTIC_KEYS = [
    "ampicillin",
    "gentamicyn",
    "cefotaxime",
    "cefotaxim",
    "cotrimoxazole",
    "cloramfenicol",
    "ceftriaxon",
    "cefixim",
    "casandoz",
    "sporetik",
    "metronidazole",
    "cethixim simp",
    "cotrimoxazole",
    "chloramphenicol",
    "cefadroxil",
]


def clean_drug_name(name):
    """Функція очищення для перевірки патернів."""
    cleaned = str(name).lower().strip()
    cleaned = re.sub(r"[^a-zA-Z\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def classify_drugs(row):
    """
    Аналізує рядок Adtype (розділяючи по рядках) ТА стовпець AB.
    Якщо рядок не є АБ чи Пробіотиком - вважаємо Іншим.
    """
    adtype_s = str(row[col_adtype]).strip()
    ab_flag = str(row[col_ab]).upper().strip()

    has_antibiotic_flag = "N"
    has_probiotic_flag = "N"
    has_other_drug_flag = "N"

    if ab_flag == "Y":
        has_antibiotic_flag = "Y"

    lines = re.split(r"\n|_x000D_", adtype_s)

    for line in lines:
        cleaned_line = clean_drug_name(line)
        if len(cleaned_line) <= 2:
            continue

        is_antibiotic = False
        is_probiotic = False

        for key in ANTIBIOTIC_KEYS:
            if re.search(r"\b" + re.escape(key) + r"\b", cleaned_line):
                has_antibiotic_flag = "Y"
                is_antibiotic = True
                break
        for key in PROBIOTIC_KEYS:
            if re.search(r"\b" + re.escape(key) + r"\b", cleaned_line):
                has_probiotic_flag = "Y"
                is_probiotic = True
                break
        if not is_antibiotic and not is_probiotic:
            has_other_drug_flag = "Y"

    return has_antibiotic_flag, has_probiotic_flag, has_other_drug_flag


df[
    [
        "Has_Antibiotic",
        "Has_Probiotic",
        "Has_Other_Drug",
    ]
] = df.apply(
    classify_drugs,
    axis=1,
    result_type="expand",
)

df_cleaned = df.dropna(subset=[col_los])


# === Завдання 4: Вплив терапії ПРОБІОТИКАМИ на кількість ліжко-днів ===
print("\n--- Завдання 4: Вплив терапії ПРОБІОТИКАМИ на кількість ліжко-днів ---")

plt.figure(figsize=(8, 5))
sns.boxplot(data=df_cleaned, x="Has_Probiotic", y=col_los)
plt.title("Вплив прийому пробіотиків на кількість ліжко-днів")
plt.xlabel("Пацієнт отримував пробіотик")
plt.ylabel("Кількість ліжко-днів")
plt.xticks(ticks=[0, 1], labels=["Ні", "Так"])
plt.tight_layout()
plt.savefig("4_Пробіотик_vs_Ліжко_дні.png")

# Тест Mann-Whitney U
group_probiotic_yes = df_cleaned[col_los][df_cleaned["Has_Probiotic"] == "Y"].dropna()
group_probiotic_no = df_cleaned[col_los][df_cleaned["Has_Probiotic"] == "N"].dropna()

print("\nПеревірка груп для тесту:")
mean_yes = group_probiotic_yes.mean() if not group_probiotic_yes.empty else "N/A"
mean_no = group_probiotic_no.mean() if not group_probiotic_no.empty else "N/A"
print(
    f"  Група 'Пробіотик=Y': {len(group_probiotic_yes)} осіб. (Середні ліжко-дні: {mean_yes if isinstance(mean_yes, str) else f'{mean_yes:.2f}'})"
)
print(
    f"  Група 'Пробіотик=N': {len(group_probiotic_no)} осіб. (Середні ліжко-дні: {mean_no if isinstance(mean_no, str) else f'{mean_no:.2f}'})"
)

stat, p_val = stats.mannwhitneyu(
    group_probiotic_yes, group_probiotic_no, alternative="two-sided"
)
print("\nТест Mann-Whitney U (Пробіотик 'Y' vs 'N'):")
print(f"  U-statistic = {stat:.3f}")
print(f"  p-value = {p_val:.4f}")
if p_val < 0.05:
    print("  Результат: Знайдено статистично значущу різницю.")
else:
    print("  Результат: Не знайдено статистично значущої різниці.")

print("\n--- Завершення аналізу Завдання 4 ---")
