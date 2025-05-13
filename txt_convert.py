import pandas as pd

# Load the CSV
df = pd.read_csv("columbia_buildings_detailed.csv")
df.fillna("N/A", inplace=True)

# Format each building into a readable paragraph
lines = []
for _, row in df.iterrows():
    building_info = f"""
Building Name: {row['Building Name']}
Description: {row['Description']}
Built In: {row['Built in']}
Entrance Location: {row['Entrance Location']}
Residential Floors: {row['Number of Residential Floors']}
Residential Apartments: {row['Number of Residential Apartments']}
Accessibility: {row['Accessible']}
Air Conditioning: {row['Air Conditioning']}
Laundry Location: {row['Laundry Location']}
Laundry Hours: {row['Laundry Hours']}
Trash Disposal Location: {row['Trash & Recycling Disposal Location']}
Trash Pick-up Days: {row['Trash Pick-up Days']}
Recycling Pick-up Days: {row['Recycling Pick-up Days']}
Cable Provider: {row['Cable Provider']}
Fire Safety Plan: {row['Fire Safety Plan']}
Superintendent: {row['Superintendent']}
Backup Superintendent: {row['Back-up Superintendent']}
Director of Asset Management: {row['Director of Asset Management']}
Portfolio Manager: {row['Portfolio Manager']}
Building Amenities: {row['Building Amenities']}
URL: {row['URL']}
{'-'*80}
"""
    lines.append(building_info)

# Save to TXT
output_file = "columbia_buildings_kb.txt"
with open(output_file, "w") as f:
    f.writelines(lines)

print(f"✅ File saved as: {output_file}")
