#dodaje do zdjęć watermarki

import os
from datetime import datetime
import random
import cv2
import yaml
import numpy as np

def get_file_date(file_path):
    """Return the modification date of the file in MM_RRRR format."""
    timestamp = os.path.getmtime(file_path)
    date = datetime.fromtimestamp(timestamp)
    return date.strftime("%m_%Y")

def get_random_color():
    """Generate a random color."""
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (128, 0, 128),  # Purple
        (0, 128, 128),  # Teal
        (128, 128, 0)   # Olive
        # Add more colors as needed
    ]
    return random.choice(colors)

def calculate_distance(pos1, pos2):
    """Calculate Euclidean distance between two positions."""
    return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def is_position_far_enough(new_pos, used_positions, min_distance):
    """Check if new position is far enough from used positions."""
    for pos in used_positions:
        if calculate_distance(new_pos, pos) < min_distance:
            return False
    return True

def add_watermark(image_path, output_path):
    """Add watermark texts to an image using OpenCV."""
    # Load the image
    image = cv2.imread(image_path)
    image_height, image_width = image.shape[:2]
    
    # Read file date and name
    file_date = get_file_date(image_path)
    file_name = os.path.basename(image_path)
    
    # List of watermark texts
    watermark_texts = [
        "MapMarket.pl",
        f"Data pliku: {file_date}",
        f"Nazwa pliku: {file_name}"
    ]
    
    # Adding watermarks
    used_positions = []
    min_distance = 100  # Minimum distance between watermark positions
    
    for text in watermark_texts:
        # Get text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)
        
        # Find a suitable position with enough distance from existing positions
        found_position = False
        while not found_position:
            x = random.randint(0, image_width - text_width)
            y = random.randint(text_height, image_height - baseline)
            new_pos = (x, y)
            
            if is_position_far_enough(new_pos, used_positions, min_distance):
                found_position = True
        
        # Get a random color for the text
        text_color = get_random_color()
        
        # Add watermark to image
        cv2.putText(image, text, (x, y), font, font_scale, text_color, font_thickness)
        used_positions.append(new_pos)
    
    # Save the image with watermarks
    cv2.imwrite(output_path, image)
    print(f"Znaki wodne zostały dodane do: {output_path}")

def main():
    # Input and output directories
    input_dir = r'C:\test123\tools\FotoOriginal'
    output_dir = r'C:\test123\static\foto'
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Output YAML file path
    output_file = 'temp-watermark.yml'
    yaml_data = []

    # Process each image in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg') or filename.lower().endswith('.png'):
            try:
                input_image_path = os.path.join(input_dir, filename)
                output_image_path = os.path.join(output_dir, f"{filename}")
                
                add_watermark(input_image_path, output_image_path)
                
                # Collect data for YAML output
                file_date = get_file_date(input_image_path)
                file_info = {
                    'file': filename,
                    'date': file_date
                }
                yaml_data.append(file_info)
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    # Write YAML data to file
    with open(os.path.join(output_dir, output_file), 'w') as file:
        yaml.dump(yaml_data, file, default_flow_style=False, sort_keys=False)

    # Remove YAML file if it exists
    yaml_file_path = os.path.join(output_dir, output_file)
    if os.path.exists(yaml_file_path):
        os.remove(yaml_file_path)
        print(f"Usunięto plik YAML: {yaml_file_path}")

if __name__ == '__main__':
    main()
