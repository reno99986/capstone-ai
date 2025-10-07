from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="capstone_app")

# Contoh geocoding alamat -> koordinat
location = geolocator.geocode("Institut Teknologi Kalimantan, Balikpapan")
print(location.latitude, location.longitude)

# Contoh reverse geocoding koordinat -> alamat
reverse_location = geolocator.reverse(( -1.1853, 116.8614 ))
print(reverse_location.address)
