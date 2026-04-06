import pandas as pd

# 1. LOAD THE FILE
input_file = 'Delhi_Historical_Master.csv'
output_file = 'Delhi_Final_Clean.csv'

print(f"Reading {input_file}...")
try:
    df = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"Error: Could not find {input_file}. Make sure it is in the same folder.")
    exit()

# 2. FIX TIMESTAMP
# Handles mixed date formats and sorts chronologically
df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed', dayfirst=True, errors='coerce')
df = df.dropna(subset=['Timestamp'])
df = df.sort_values('Timestamp')

# 3. RENAME COLUMNS (To match your specific requirements)
# We map the raw headers to the clean names you want
rename_map = {
    'PM2.5 (µg/m³)': 'PM2.5',
    'PM10 (µg/m³)': 'PM10',
    'NO2 (µg/m³)': 'NO2',
    'CO (mg/m³)': 'CO',
    'Ozone (µg/m³)': 'Ozone'
}
df.rename(columns=rename_map, inplace=True)

# 4. FILL MISSING VALUES ("Somehow" -> Linear Interpolation)
target_cols = ['PM2.5', 'PM10', 'NO2', 'CO', 'Ozone']

for col in target_cols:
    if col in df.columns:
        # Ensure data is numeric
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Interpolate: Fills gaps by connecting the previous and next known values
        df[col] = df[col].interpolate(method='linear', limit_direction='both')
        # Fallback: If the very first/last rows are empty, fill them
        df[col] = df[col].bfill().ffill()
    else:
        # If column is missing entirely, create it with 0s to prevent crash
        df[col] = 0

# 5. CREATE DERIVED ATTRIBUTES
df['Year'] = df['Timestamp'].dt.year
df['Month'] = df['Timestamp'].dt.month_name()
df['City'] = 'Delhi'

def get_season(m):
    if m in ['November', 'December', 'January', 'February']: return 'Winter'
    elif m in ['March', 'April', 'May', 'June']: return 'Summer'
    elif m in ['July', 'August', 'September']: return 'Monsoon'
    else: return 'Post-Monsoon'
df['Season'] = df['Month'].apply(get_season)

# Calculate AQI (Max of PM2.5 and PM10)
df['Calculated AQI'] = df[['PM2.5', 'PM10']].max(axis=1)

# 6. SELECT ONLY THE REQUESTED COLUMNS
final_columns = [
    'Timestamp', 'PM2.5', 'PM10', 'NO2', 'CO', 'Ozone', 
    'Year', 'Month', 'Season', 'Calculated AQI', 'City'
]

# Filter the dataframe
df_final = df[final_columns]

# 7. SAVE
df_final.to_csv(output_file, index=False)
print(f"Success! Created {output_file} with columns: {list(df_final.columns)}")