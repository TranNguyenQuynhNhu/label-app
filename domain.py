from datasets import load_dataset

print("Đang tải dữ liệu...")
dataset = load_dataset(
    "aisingapore/SEA-Instruct-2602",
    "Vietnamese",
    split="train"
)

df = dataset.to_pandas()

culture_domains = [
    "Social_and_Cultural_Issues",
    "Food_and_Cuisine",
    "Arts_and_Literature",
    "History_and_Heritage",
    "Sports_and_Fitness",
    "Daily_Life_and_Personal",
    "Government_and_Politics",
    "Parenting_and_Family",
    "Legal_Rights_and_Access",
    "Education",
    "Media_and_Entertainment",
    "Superstitions_Myth_and_Folklore",
    "Travel_and_Tourism",
    "Traditional_Medicine_and_Alternative_Healing",
    "Internet_and_Digital_Culture",
    "Agriculture_and_Fishing",
    "Religion_and_Belief",
    "Law_and_Justice",
    "Migrant_Worker_Expat_and_Student_Life",
]

count = df["prompt_primary_domain"].isin(culture_domains).sum()
print(f"Số record thuộc các domain Is_Culture = Y: {count}")