"""
Add golden_truth column to output_for_eval.csv
"""
import pandas as pd

# Read CSV
df = pd.read_csv('output_for_eval.csv', delimiter=';')

print(f"📊 Processing {len(df)} rows...")

# Create golden_truth column
def create_golden_truth(row):
    """Generate golden truth description from row data"""
    
    nama = row.get('nama', 'N/A')
    alamat = row.get('alamat', 'alamat tidak tersedia')
    kecamatan = row.get('nmkec', 'N/A')
    kabupaten = row.get('nmkab', 'Balikpapan')
    provinsi = row.get('nmprov', 'Kalimantan Timur')
    kategori = row.get('kategori', '')
    produk = row.get('produk_utama', '')
    
    # Build description
    parts = [f"{nama} adalah"]
    
    # Add category/product if available
    if kategori and str(kategori) != 'nan':
        parts.append(f"usaha {kategori.lower()}")
    elif produk and str(produk) != 'nan':
        parts.append(f"usaha yang menjual {produk.lower()}")
    else:
        parts.append("usaha")
    
    # Add location
    parts.append(f"yang berlokasi di {alamat}")
    
    # Add kecamatan, kabupaten, provinsi
    location_parts = []
    if kecamatan and str(kecamatan) != 'nan':
        location_parts.append(f"Kecamatan {kecamatan}")
    if kabupaten and str(kabupaten) != 'nan':
        location_parts.append(kabupaten)
    if provinsi and str(provinsi) != 'nan':
        location_parts.append(provinsi)
    
    if location_parts:
        parts.append(f", {', '.join(location_parts)}")
    
    parts.append(".")
    
    return " ".join(parts)

# Apply to all rows
df['golden_truth'] = df.apply(create_golden_truth, axis=1)

# Save back
df.to_csv('output_for_eval.csv', sep=';', index=False)

print(f"✅ Added 'golden_truth' column to {len(df)} rows")
print(f"\n📝 Sample golden_truth:")
print(f"{df['golden_truth'].iloc[0][:200]}...")
print(f"\n💾 Saved to: output_for_eval.csv")
