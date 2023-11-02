import requests
import os
import re
import argparse
import time
import string
from rich.console import Console

console = Console(highlight=False)

def cprint(color, content):
    console.print(f"[bold {color}]{content}[/bold {color}]")

# Function to download and save the XML file
def download_xml(clothing_id):
    url = f'https://assetdelivery.roblox.com/v1/asset/?id={clothing_id}'
    response = requests.get(url)

    if response.status_code == 200:
        # Create a directory named 'xml_temp' if it doesn't exist
        if not os.path.exists('xml_temp'):
            os.mkdir('xml_temp')

        with open(f'xml_temp/{clothing_id}.xml', 'wb') as file:
            file.write(response.content)
        cprint('green', f'Successfully downloaded temporary file: {clothing_id}.xml')
    else:
        cprint('red', f'Failed to download temporary file: {clothing_id}')

# Function to extract the new ID from the XML file
def extract_new_id(xml_file_path):
    with open(xml_file_path, 'r') as file:
        xml_content = file.read()

    # Use regex to extract the new ID from the <url> tag
    match = re.search(r'<url>.*\?id=(\d+)</url>', xml_content)
    if match:
        return match.group(1)
    else:
        return None

# Function to get the name of the item using ITEM_ID with retries
def get_item_name(item_id):
    while True:
        url = f'https://economy.roblox.com/v2/assets/{item_id}/details'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            name = data.get('Name', 'Unknown')
            return name
        else:
            cprint('yellow', f'Failed to get item name for ITEM_ID: {item_id}, Retrying...')
            time.sleep(2)

# Function to sanitize a string
def sanitize_filename(name):
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(char for char in name if char in valid_chars)

# Function to avoid overwriting
def add_suffix_if_exists(file_name):
    base_name, ext = os.path.splitext(file_name)
    index = 1
    while os.path.exists(file_name):
        file_name = f'{base_name}_{index}{ext}'
        index += 1
    return file_name

def download_clothing_image(clothing_id, new_id):
    # Get the name of the item using new_id, fallback to clothing_id
    item_name = get_item_name(new_id)

    if item_name == 'Unknown':
        item_name = clothing_id

    item_name = sanitize_filename(item_name)
    file_name = f'clothes/{item_name}.png'
    file_name = add_suffix_if_exists(file_name)

    url = f'https://assetdelivery.roblox.com/v1/asset/?id={new_id}'
    response = requests.get(url)
    
    if response.status_code == 200:
        # Create a directory named 'clothes' if it doesn't exist
        if not os.path.exists('clothes'):
            os.mkdir('clothes')

        # Save the image as a PNG file with the sanitized item name
        with open(file_name, 'wb') as file:
            file.write(response.content)
        cprint('green', f'Successfully downloaded {file_name}')
    else:
        cprint('red', f'Failed to download {file_name}')

if not os.path.exists('xml_temp'):
    os.mkdir('xml_temp')

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Download.')
parser.add_argument('file', nargs='?', help='optional')
args = parser.parse_args()

if args.file:
    # Check if the argument is a clothing ID
    if args.file.isdigit():
        clothing_id = args.file
        download_xml(clothing_id)

        xml_file_path = f'xml_temp/{clothing_id}.xml'
        new_id = extract_new_id(xml_file_path)

        if new_id:
            download_clothing_image(clothing_id, new_id)
            os.remove(xml_file_path)
        else:
            cprint('red', f'Failed to extract new ID from {clothing_id}.xml')
    else:
        with open(args.file, 'r') as file:
            lines = file.readlines()
        
        os.system("cls")
        
        for line in lines:
            if line.startswith('https://www.roblox.com/catalog/'):
                match = re.search(r'/(\d+)/', line)
                if match:
                    clothing_id = match.group(1)
                else:
                    cprint('red', f'Failed to extract clothing ID from URL: {line}')
                    continue
            else:
                clothing_id = line.strip()  # Assuming each line in the file is a clothing ID

            download_xml(clothing_id)

            xml_file_path = f'xml_temp/{clothing_id}.xml'
            new_id = extract_new_id(xml_file_path)

            if new_id:
                download_clothing_image(clothing_id, new_id)
                os.remove(xml_file_path)
            else:
                cprint('red', f'Failed to extract new ID from {clothing_id}.xml')
else:
    clothing_id = input('Enter the clothing ID or URL: ')
    if clothing_id.startswith('https://www.roblox.com/catalog/'):
        match = re.search(r'/(\d+)/', clothing_id)
        if match:
            clothing_id = match.group(1)
        else:
            cprint('red', 'Failed to extract clothing ID from the provided URL.')
    download_xml(clothing_id)
    xml_file_path = f'xml_temp/{clothing_id}.xml'
    new_id = extract_new_id(xml_file_path)

    if new_id:
        download_clothing_image(clothing_id, new_id)
        os.remove(xml_file_path) # Change this if you want to keep the temporary XML files

cprint('cyan', 'Finished downloading clothing items.')
