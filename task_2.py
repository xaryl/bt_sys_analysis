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
    "aampicillin",
    "ab ampicillin",
    "amoxicilin",
    "amoxillin inj",
    "amoxson",
    "ampi",
    "ampi inj",
    "ampicilin",
    "ampicilin inj",
    "ampicilliin",
    "ampicillin",
    "ampicillin inj",
    "ampicillin injeksi",
    "ampicillin iv",
    "ampiocilin",
    "ampiullin",
    "antibiotik",
    "antibiotik ampi chloram intakranial",
    "antibiotik ampicillin",
    "antibiotik ampicillin ijn",
    "antibiotik ampicillin inj",
    "antibiotik cefalaxi",
    "bactoprim combi syr",
    "cefadroxil",
    "cefhriaxoa",
    "cefixime",
    "cefixime syr",
    "cefotacime",
    "cefotax inj",
    "cefotaxil",
    "cefotaxim",
    "cefotaxim inj",
    "cefotaxime",
    "cefotaxin",
    "ceftriaxominj",
    "ceftriaxon",
    "ceftriaxone",
    "cetriaxon",
    "chlnamprnicol",
    "chloramphenicol",
    "ciprofloxacin",
    "clirolanfenicol",
    "cloramfenicol",
    "clorampenicol",
    "cloramphenicol",
    "cotrimoxazole",
    "cotrimoxazole syr",
    "ehloramfenise",
    "genta",
    "gentamia inj",
    "gentamic inj",
    "gentamicin",
    "gentamicin inj",
    "gentamicyn",
    "gentamiexa",
    "gentamisin",
    "gentammicin",
    "gentamycin",
    "halmycin syr",
    "inj ampicillin",
    "inj cefotaxim",
    "inj cefotaxime",
    "inj ceftriaxon iv",
    "kotri",
    "metromidazole",
    "metronidazole",
    "pelastin",
    "phenicol",
    "protaxim",
    "rimactazid",
    "sampicillin",
    "sanpicilin",
    "sanpicilin syr",
    "sanpicillin x",
    "sanprima",
    "sanprima syr",
    "sefotaxim",
    "sporetik syr",
    "thyesmicin syr",
    "zidiped ganti ampicillin",
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

cols_treatment = ["Has_Antibiotic", "Has_Probiotic", "Has_Other_Drug"]

df_cleaned = df.dropna(subset=[col_los])

df_cleaned = df_cleaned.copy()
df_cleaned["Treatment_Combo"] = df_cleaned.apply(
    lambda row: "+".join(sorted([col for col in cols_treatment if row[col] == "Y"])),
    axis=1,
)
df_cleaned["Treatment_Combo"] = df_cleaned["Treatment_Combo"].replace(
    "", "Інші препарати"
)
df_cleaned["Treatment_Combo"] = df_cleaned["Treatment_Combo"].str.replace(
    "Has_Antibiotic", "Антибіотик"
)
df_cleaned["Treatment_Combo"] = df_cleaned["Treatment_Combo"].str.replace(
    "Has_Probiotic", "Пробіотик"
)
df_cleaned["Treatment_Combo"] = df_cleaned["Treatment_Combo"].str.replace(
    "Has_Other_Drug", "Інші препарати"
)


# === Завдання 2: Залежність між видом лікування та кількістю ліжко-днів ===
print("\n--- Завдання 2: Вид лікування vs Кількість ліжко-днів ---")

plt.figure(figsize=(12, 8))
order = df_cleaned.groupby("Treatment_Combo")[col_los].median().sort_values().index
sns.boxplot(
    data=df_cleaned,
    x=col_los,
    y="Treatment_Combo",
    order=order,
)

plt.title("Залежність кількості ліжко-днів від типу лікування")
plt.xlabel("Кількість ліжко-днів")
plt.ylabel("Тип лікування")
plt.tight_layout()
plt.savefig("2_Тип_лікування_vs_Ліжко_дні.png")

# Статистичний тест (Крускал-Уолліс)
groups = df_cleaned["Treatment_Combo"].unique()
samples = [
    df_cleaned[col_los][df_cleaned["Treatment_Combo"] == g].dropna() for g in groups
]
h_val, p_val = stats.kruskal(*samples)
print("\nТест Крускала-Уолліса:")
print(f"  H-statistic = {h_val:.3f}")
print(f"  p-value = {p_val:.4f}")
if p_val < 0.05:
    print("  Результат: Знайдено статистично значущу різницю між групами.")
else:
    print("  Результат: Не знайдено статистично значущої різниці між групами.")

print("\n--- Завершення аналізу Завдання 2 ---")
