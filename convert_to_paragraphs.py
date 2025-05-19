from pathlib import Path

# --------- Step 1: Load the text file ---------
input_path = "columbia_buildings_kb.txt"  # <- Replace with your file path
output_path = "columbia_buildings_paragraphs.txt"

with open(input_path, "r", encoding="utf-8") as file:
    raw_text = file.read()

# --------- Step 2: Split into building blocks ---------
building_blocks = raw_text.strip().split("--------------------------------------------------------------------------------")

# --------- Step 3: Convert key-value blocks to paragraph ---------
def parse_block(block):
    lines = block.strip().split('\n')
    data = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data

def to_paragraph(data):
    name = data.get('Building Name', 'This building')
    year = data.get('Built In', 'an unknown year')
    location = data.get('Entrance Location', 'an unspecified location')
    description = data.get('Description', '')
    floors = data.get('Residential Floors', 'unknown floors')
    apartments = data.get('Residential Apartments', 'unknown apartments')
    access = 'accessible' if data.get('Accessibility', 'No') == 'Yes' else 'not accessible'
    amenities = data.get('Building Amenities', 'no listed amenities')
    laundry_loc = data.get('Laundry Location', 'an unspecified location')
    laundry_hours = data.get('Laundry Hours', 'unspecified hours')
    trash_loc = data.get('Trash Disposal Location', 'unspecified location')
    trash_days = data.get('Trash Pick-up Days', 'unspecified days')
    recycle_days = data.get('Recycling Pick-up Days', 'unspecified days')
    cable = data.get('Cable Provider', 'unspecified')
    super_ = data.get('Superintendent', 'unspecified')
    portfolio_mgr = data.get('Portfolio Manager', 'unspecified')
    url = data.get('URL', 'N/A')

    return (
        f"{name} is a Columbia Residential building located at {location}. Built in {year}, "
        f"it houses residents in {apartments} across {floors}. The building is {access} and offers amenities such as {amenities}. "
        f"{description} Laundry is located {laundry_loc} and available during {laundry_hours}. "
        f"Trash disposal is in the {trash_loc}, with pickups on {trash_days} and recycling on {recycle_days}. "
        f"Cable service is provided by {cable}. The superintendent is {super_}, and the portfolio manager is {portfolio_mgr}. "
        f"More information: {url}."
    )

# --------- Step 4: Build paragraphs ---------
paragraphs = []
for block in building_blocks:
    data = parse_block(block)
    if data:
        para = to_paragraph(data)
        paragraphs.append(para)

# --------- Step 5: Save to output file ---------
with open(output_path, "w", encoding="utf-8") as out:
    for p in paragraphs:
        out.write(p + "\n\n---\n\n")

print(f"✅ Done! {len(paragraphs)} paragraphs saved to {output_path}")

