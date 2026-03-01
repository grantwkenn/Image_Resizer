from PIL import Image
import piexif
import os
from pathlib import Path
import filetype
import folium
from folium import plugins

# Input path
input_path = "input/03_March_2025"

# Array to store GPS data mapped to timestamps
gps_data = []

def get_timestamp(exif_data):
    """Extract timestamp from EXIF data"""
    try:
        # Try to get DateTime from Exif IFD
        if "Exif" in exif_data and 36867 in exif_data["Exif"]:  # 36867 is DateTimeOriginal
            timestamp = exif_data["Exif"][36867].decode()
            return timestamp
        # Fall back to DateTime in IFD 0
        elif 0 in exif_data and 306 in exif_data[0]:  # 306 is DateTime
            timestamp = exif_data[0][306].decode()
            return timestamp
    except Exception as e:
        print(f"Error extracting timestamp: {e}")
    return None

def convert_gps_coords(gps_data):
    """Convert GPS coordinates from EXIF format to decimal degrees"""
    try:
        # GPS data is stored as tuples of (numerator, denominator)
        degrees = gps_data[0][0] / gps_data[0][1]
        minutes = gps_data[1][0] / gps_data[1][1]
        seconds = gps_data[2][0] / gps_data[2][1]
        
        decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
        return decimal_degrees
    except Exception as e:
        print(f"Error converting GPS coordinates: {e}")
    return None

def get_gps_data(exif_data):
    """Extract GPS data from EXIF"""
    try:
        if "GPS" not in exif_data:
            return None
        
        gps_ifd = exif_data["GPS"]
        
        # GPS tags: 2=North/South Latitude, 4=East/West Longitude, 6=Altitude
        latitude = None
        longitude = None
        altitude = None
        lat_ref = None
        lon_ref = None
        
        if 2 in gps_ifd:  # Latitude
            latitude = convert_gps_coords(gps_ifd[2])
            lat_ref = gps_ifd.get(1, None)  # N or S
            if lat_ref and lat_ref == b'S':
                latitude = -latitude
        
        if 4 in gps_ifd:  # Longitude
            longitude = convert_gps_coords(gps_ifd[4])
            lon_ref = gps_ifd.get(3, None)  # E or W
            if lon_ref and lon_ref == b'W':
                longitude = -longitude
        
        if 6 in gps_ifd:  # Altitude
            alt_data = gps_ifd[6]
            altitude = alt_data[0] / alt_data[1]
        
        if latitude is not None and longitude is not None:
            return {
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude
            }
    except Exception as e:
        print(f"Error extracting GPS data: {e}")
    
    return None

def process_photos(input_dir):
    """Walk through directory and extract GPS data"""
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            input_file_path = os.path.join(root, file)
            
            if filetype.is_image(input_file_path):
                try:
                    with Image.open(input_file_path) as img:
                        exif_bytes = img.info.get("exif", None)
                        
                        if exif_bytes:
                            exif_data = piexif.load(exif_bytes)
                            timestamp = get_timestamp(exif_data)
                            gps_info = get_gps_data(exif_data)
                            
                            if gps_info:
                                gps_data.append({
                                    "file": input_file_path,
                                    "timestamp": timestamp,
                                    "latitude": gps_info["latitude"],
                                    "longitude": gps_info["longitude"],
                                    "altitude": gps_info["altitude"]
                                })
                                print(f"File: {input_file_path}")
                                print(f"Timestamp: {timestamp}")
                                print(f"Lat: {gps_info['latitude']}, Lon: {gps_info['longitude']}, Alt: {gps_info['altitude']}")
                                print()
                except Exception as e:
                    print(f"Error processing {input_file_path}: {e}")

def create_map(gps_data):
    """Create an interactive map with GPS locations"""
    if not gps_data:
        print("No GPS data to map")
        return
    
    # Calculate center of map (average of all coordinates)
    avg_lat = sum(entry["latitude"] for entry in gps_data) / len(gps_data)
    avg_lon = sum(entry["longitude"] for entry in gps_data) / len(gps_data)
    
    # Create map centered on average location
    map_obj = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=13,
        tiles="OpenStreetMap"
    )
    
    # Add markers for each GPS location
    for idx, entry in enumerate(gps_data):
        altitude_str = f"{entry['altitude']:.1f}m" if entry['altitude'] else 'N/A'
        popup_text = f"""
        <b>File:</b> {Path(entry['file']).name}<br>
        <b>Timestamp:</b> {entry['timestamp']}<br>
        <b>Lat:</b> {entry['latitude']:.6f}<br>
        <b>Lon:</b> {entry['longitude']:.6f}<br>
        <b>Alt:</b> {altitude_str}
        """
        
        folium.Marker(
            location=[entry["latitude"], entry["longitude"]],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"Photo {idx + 1}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(map_obj)
    
    # Add a line connecting all points in order
    if len(gps_data) > 1:
        coords = [[entry["latitude"], entry["longitude"]] for entry in gps_data]
        folium.PolyLine(coords, color="red", weight=2, opacity=0.7).add_to(map_obj)
    
    # Save map
    map_file = "gps_map.html"
    map_obj.save(map_file)
    print(f"\nMap created: {map_file}")
    print(f"Open this file in a web browser to view the interactive map")

# Process photos
process_photos(input_path)

# Print summary
print(f"\nFound {len(gps_data)} photos with GPS data")
print("\nGPS Data Array:")
for entry in gps_data:
    print(entry)

# Create map
if gps_data:
    create_map(gps_data)
