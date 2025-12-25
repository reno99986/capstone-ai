"""
Fix golden_truth column with proper descriptions
"""
import pandas as pd

# Read CSV
df = pd.read_csv('output_for_eval.csv', delimiter=';')

print(f"📊 Processing {len(df)} rows...")

def create_proper_golden_truth(row):
    """Generate golden truth from available data"""
    
    # Get all available data
    nama = row.get('nama tempat', '')
    alamat = row.get('alamat', '')
    kategori = row.get('kategori', '')
    produk = row.get('produk_utama', '')
    kecamatan = row.get('nmkec', '')
    kabupaten = row.get('nmkab', '')
    provinsi = row.get('nmprov', '')
    
    # Convert to string and handle NaN
    nama = str(nama) if pd.notna(nama) else ''
    alamat = str(alamat) if pd.notna(alamat) else ''
    kategori = str(kategori) if pd.notna(kategori) else ''
    produk = str(produk) if pd.notna(produk) else ''
    kecamatan = str(kecamatan) if pd.notna(kecamatan) else ''
    kabupaten = str(kabupaten) if pd.notna(kabupaten) else 'Balikpapan'
    provinsi = str(provinsi) if pd.notna(provinsi) else 'Kalimantan Timur'
    
    # Clean up 'nan' strings
    if nama == 'nan' or not nama.strip(): nama = ''
    if alamat == 'nan' or not alamat.strip(): alamat = ''
    if kategori == 'nan' or not kategori.strip(): kategori = ''
    if produk == 'nan' or not produk.strip(): produk = ''
    if kecamatan == 'nan' or not kecamatan.strip(): kecamatan = ''
    
    # Build description
    if not nama:
        return "Informasi usaha tidak lengkap."
    
    parts = [f"{nama} adalah"]
    
    # Add type/category
    if kategori:
        parts.append(f"usaha {kategori.lower()}")
    elif produk:
        parts.append(f"usaha yang bergerak di bidang {produk.lower()}")
    else:
        parts.append("usaha")
    
    # Add location
    if alamat:
        parts.append(f"yang berlokasi di {alamat}")
    
    # Add administrative location
    location_parts = []
    if kecamatan:
        location_parts.append(f"Kecamatan {kecamatan}")
    if kabupaten:
        location_parts.append(kabupaten)
    if provinsi:
        location_parts.append(provinsi)
    
    if location_parts:
        if alamat:
            parts.append(f", {', '.join(location_parts)}")
        else:
            parts.append(f"yang berlokasi di {', '.join(location_parts)}")
    
    parts.append(".")
    
    return " ".join(parts)

# Apply to all rows
print("🔧 Generating golden_truth for all rows...")
df['golden_truth'] = df.apply(create_proper_golden_truth, axis=1)

# Count how many were fixed
n_fixed = (df['golden_truth'] != "Informasi usaha tidak lengkap.").sum()

# Save
df.to_csv('output_for_eval.csv', sep=';', index=False)

print(f"✅ Fixed {n_fixed}/{len(df)} rows")
print(f"\n📝 Sample golden_truth:")
for i in range(min(3, len(df))):
    print(f"\n{i+1}. {df['nama tempat'].iloc[i]}")
    print(f"   → {df['golden_truth'].iloc[i][:150]}...")

print(f"\n💾 Saved to: output_for_eval.csv")
