import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import re
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer

# Ігнорувати попередження
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

df = pd.read_excel("data.xlsx")

# Ключові стовпці
col_los = "Кількість ліжко-днів"
col_dehydration = "Dehydration"
col_temperature = "Temperature"
col_vomiting = "Vomiting"
col_rotavirus = "Ротавірус"
col_adtype = "Adtype"
col_ab = "AB"

df[col_los] = pd.to_numeric(df[col_los], errors="coerce")
df[col_temperature] = pd.to_numeric(df[col_temperature], errors="coerce")
df[col_vomiting] = pd.to_numeric(df[col_vomiting], errors="coerce")

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

df[col_rotavirus] = df[col_rotavirus].fillna("N")
df[col_rotavirus] = df[col_rotavirus].astype(str).str.strip().str.upper()
df[col_rotavirus] = df[col_rotavirus].apply(lambda x: "Y" if x == "Y" else "N")

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
    # Видаляємо лише спецсимволи та цифри, залишаючи літери та пробіли
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

    # Перевірка стовпця AB
    if ab_flag == "Y":
        has_antibiotic_flag = "Y"

    # Розділяємо Adtype на рядки
    lines = re.split(r"\n|_x000D_", adtype_s)

    for line in lines:
        cleaned_line = clean_drug_name(line)

        # Пропускаємо пусті або дуже короткі рядки після очищення
        if len(cleaned_line) <= 2:
            continue

        is_antibiotic = False
        is_probiotic = False

        # Перевіряємо наявність АБ
        for key in ANTIBIOTIC_KEYS:
            if re.search(r"\b" + re.escape(key) + r"\b", cleaned_line):
                has_antibiotic_flag = "Y"
                is_antibiotic = True
                break  # Якщо це антибіотик, далі ключі АБ не шукаємо

        # Перевіряємо наявність Пробіотиків
        for key in PROBIOTIC_KEYS:
            if re.search(r"\b" + re.escape(key) + r"\b", cleaned_line):
                has_probiotic_flag = "Y"
                is_probiotic = True
                break  # Якщо це пробіотик, далі ключі ПБ не шукаємо

        # Якщо рядок НЕ є ані АБ, ані Пробіотиком - це Інший препарат
        if not is_antibiotic and not is_probiotic:
            has_other_drug_flag = "Y"
            # Немає break, бо наступний рядок може бути АБ або Пробіотиком

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

df["Dehydration_Num"] = (
    df[col_dehydration]
    .map({"No dehydration": 0, "Mild dehydration": 1, "Severe dehydration": 2})
    .fillna(0)
)
temp_imputer = SimpleImputer(strategy="median")
df["Temperature_Num"] = temp_imputer.fit_transform(df[[col_temperature]])
vomit_imputer = SimpleImputer(strategy="median")
df["Vomiting_Num"] = vomit_imputer.fit_transform(df[[col_vomiting]])
df["Rotavirus_Num"] = df[col_rotavirus].apply(lambda x: 1 if x == "Y" else 0)

severity_features = [
    "Dehydration_Num",
    "Temperature_Num",
    "Vomiting_Num",
    "Rotavirus_Num",
]
df_severity = df[severity_features].copy()

df_scaled = MinMaxScaler().fit_transform(df_severity)
df_scaled = pd.DataFrame(df_scaled, columns=severity_features, index=df.index)

df["Severity_Index"] = df_scaled.sum(axis=1)

severity_group_labels = [
    "Низька важкість",
    "Середня важкість",
    "Висока важкість",
]
df["Severity_Group_Scaled"] = pd.qcut(
    df["Severity_Index"],
    q=3,
    labels=severity_group_labels,
    duplicates="drop",
)
print("Розподіл пацієнтів за масштабованою шкалою важкості:")
severity_counts = df["Severity_Group_Scaled"].value_counts().reset_index()
severity_counts.columns = ["Група важкості", "Кількість"]
print(severity_counts.to_markdown(index=False, numalign="left", stralign="left"))


df_cleaned = df.dropna(subset=[col_los])
print(f"\nДані фінально очищено. {len(df_cleaned)} рядків доступно для аналізу.")

df_cleaned = df_cleaned.copy()
df_cleaned["Treatment_Combo"] = df_cleaned.apply(
    lambda row: "+".join(sorted([col for col in cols_treatment if row[col] == "Y"])),
    axis=1,
)
df_cleaned["Treatment_Combo"] = df_cleaned["Treatment_Combo"].replace(
    "",
    "Інші препарати",
)
df_cleaned["Treatment_Combo"] = df_cleaned["Treatment_Combo"].str.replace(
    "Has_Antibiotic", "Антибіотик"
)
df_cleaned["Treatment_Combo"] = df_cleaned["Treatment_Combo"].str.replace(
    "Has_Probiotic", "Пробіотик"
)
df_cleaned["Treatment_Combo"] = df_cleaned["Treatment_Combo"].str.replace(
    "Has_Other_Drug",
    "Інші препарати",
)


# === Завдання 5: Створення окремих графіків ===
print("\n--- Завдання 5: Створення окремих графіків за групами важкості ---")

existing_severity_groups = df_cleaned["Severity_Group_Scaled"].unique()

for severity_group in severity_group_labels:
    print(f"Створення графіка для групи: {severity_group}")

    df_subset = df_cleaned[df_cleaned["Severity_Group_Scaled"] == severity_group]

    print(f"Статистика (ліжко-дні) для групи '{severity_group}':")

    stats_df = df_subset.groupby("Treatment_Combo")[col_los].agg(
        Середнє="mean",
        Медіана="median",
        Кількість="count",
    )
    stats_df = stats_df.sort_values(by="Медіана")
    stats_df["Середнє"] = stats_df["Середнє"].round(2)
    print(stats_df.to_markdown(numalign="left", stralign="left"))

    plot_order = (
        df_subset.groupby("Treatment_Combo")[col_los].median().sort_values().index
    )

    plt.figure(figsize=(10, 8))

    g = sns.boxplot(
        data=df_subset,
        x=col_los,
        y="Treatment_Combo",
        order=plot_order,
    )

    g.set(xlim=(0, 25))

    plt.title(f"Ліжко-дні за типом лікування ({severity_group})")
    plt.xlabel("Кількість ліжко-днів")
    plt.ylabel("Тип лікування")

    plt.tight_layout()

    filename = f"5_Важкість_{severity_group.replace(' ', '_').lower()}.png"
    plt.savefig(filename)
    print(f"Збережено графік: '{filename}'")

print("\n--- Завершення аналізу Завдання 5 ---")

# df_cleaned.to_excel("data_cleaned.xlsx")
