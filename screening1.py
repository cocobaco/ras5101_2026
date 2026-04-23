"""
RAS5101 Workshop: Intro to Data Analysis with Python
Focus: Processing XRF Screening Results for Biofortification
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. SETUP ---
N_SD = 2
WEIGHT_MIN = 2.0
INPUT_FILE = 'data/Mockup_XRF_Screening.xlsx'
OUTPUT_FILE = 'data/processed/Identified_Mutants_Report.xlsx'

# --- 2. LOAD & CLEAN ---
df_300 = pd.read_excel(INPUT_FILE, sheet_name='M4-300 Gy')
df_0 = pd.read_excel(INPUT_FILE, sheet_name='M4-0 Gy')

df_300['Dose'], df_0['Dose'] = 300, 0
df = pd.concat([df_300, df_0])

# Keep only samples with valid weights
df_clean = df[df['Weight (g)'] >= WEIGHT_MIN]

# --- 3. SCREENING LOGIC ---
# Calculate thresholds from the 0 Gy control population
stats = df_clean[df_clean['Dose'] == 0]['Fe ppm calc'].agg(['mean', 'std'])
threshold = stats['mean'] + (N_SD * stats['std'])

# Select the high-Fe mutants from the treated group
mutants = df_clean[(df_clean['Dose'] == 300) & (df_clean['Fe ppm calc'] > threshold)]

# --- 4. EXPORT RESULTS ---
# This recreates the 'output' logic from the original research script
with pd.ExcelWriter(OUTPUT_FILE) as writer:
    mutants.to_excel(writer, sheet_name='High_Fe_Mutants', index=False)
    # Also save the summary stats for reference
    summary_stats = df_clean.groupby('Dose')[['Fe ppm calc', 'Zn ppm calc']].describe()
    summary_stats.to_excel(writer, sheet_name='Statistical_Summary')

print(f"Analysis Complete. {len(mutants)} mutants saved to {OUTPUT_FILE}")

# --- 5. VISUALIZATION ---
plt.figure(figsize=(10, 6))
sns.boxplot(data=df_clean, x='Dose', y='Fe ppm calc', palette='light:b')
plt.axhline(threshold, color='red', linestyle='--', label='Selection Threshold')
plt.title('Screening Results: Iron Concentration by Dose')
plt.legend()
plt.show()