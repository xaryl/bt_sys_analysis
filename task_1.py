import pandas as pd
import warnings
import re

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

df = pd.read_excel("data.xlsx")

col_adtype = "Adtype"
col_ab = "AB"
col_los = "Кількість ліжко-днів"

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

# === Завдання 1: Дослідити комбінації лікування ===
print(
    f"\n--- Завдання 1: Аналіз комбінацій лікування (на {len(df_cleaned)} пацієнтах) ---"
)

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


print("\nКількість осіб за типом лікування:")
treatment_counts = df_cleaned["Treatment_Combo"].value_counts()
treatment_counts_df = treatment_counts.reset_index()
treatment_counts_df.columns = ["Тип лікування", "Кількість"]
print(treatment_counts_df.to_markdown(index=False, numalign="left", stralign="left"))

print("\nЗагальна кількість за окремими категоріями:")
print(f"Отримували Антибіотики: {len(df_cleaned[df_cleaned['Has_Antibiotic'] == 'Y'])}")
print(f"Отримували Пробіотик: {len(df_cleaned[df_cleaned['Has_Probiotic'] == 'Y'])}")
print(
    f"Отримували Інші препарати: {len(df_cleaned[df_cleaned['Has_Other_Drug'] == 'Y'])}"
)

print("\n--- Завершення аналізу Завдання 1 ---")
