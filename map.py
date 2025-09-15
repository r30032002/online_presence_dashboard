import pandas as pd
import requests
import time

# Read CSV as single column
df_raw = pd.read_csv("online_presence_dashboard/data/processed/joint_ils_aid.csv", header=None)
# Skip the first row if it’s junk
df_raw = df_raw.iloc[2:]

# Split the single column by commas into proper columns
# Limit to 4 splits to handle addresses with commas
df_split = df_raw[0].str.split(",", n=3, expand=True)
df_split.columns = ["Store", "Address", "Phone Number", "Type"]

print(df_split.head())

# -------------------------
# Google Maps API key
# -------------------------
API_KEY = "AIzaSyCYRD85uKiGXVclcAkW5zIrKSlRPV2H2pI"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# -------------------------
# Function to geocode a single address
# -------------------------
def geocode_address(address):
    params = {
        "address": address,
        "key": API_KEY
    }
    try:
        response = requests.get(GEOCODE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            print(f"[SUCCESS] Geocoded: {address} -> ({location['lat']}, {location['lng']})")
            return location["lat"], location["lng"]
        else:
            print(f"[FAIL] Could not geocode {address}: {data['status']}")
            return None, None
    except Exception as e:
        print(f"[ERROR] Exception for {address}: {e}")
        return None, None

# -------------------------
# Loop through DataFrame
# -------------------------
lats = []
lngs = []

for idx, row in df_split.iterrows():
    address = row["Address"]
    lat, lng = geocode_address(address)
    lats.append(lat)
    lngs.append(lng)
    time.sleep(0.1)  # Small delay to avoid hitting API limits

# -------------------------
# Add coordinates to DataFrame
# -------------------------
df_split["Latitude"] = lats
df_split["Longitude"] = lngs

# -------------------------
# Save updated DataFrame
# -------------------------
df_split.to_csv("data/processed/joint_ils_aid_geocoded.csv", index=False)
print("\nGeocoding complete! Saved to joint_ils_aid_geocoded.csv")
