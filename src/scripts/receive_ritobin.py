import os
import requests
import zipfile

def download_zip(url, destination_folder):
    # Check if the destination folder exists, if not create it
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Extract the filename from the URL
    filename = url.split('/')[-1]
    file_path = os.path.join(destination_folder, filename)

    # Download the file
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Open the file in write-binary mode
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                # Filter out keep-alive new chunks
                if chunk:  
                    file.write(chunk)
        print(f"Successfully downloaded {file_path}")
        
        # Check if the file is actually a .zip file by trying to open it
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                print("File is a valid zip archive.")
        except zipfile.BadZipFile:
            print("Warning: The file does not appear to be a valid zip archive.")
    
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.ConnectionError:
        print("Connection error. Make sure you have an active internet connection.")
    except requests.Timeout:
        print("The request timed out.")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

def unzip_file(file_path, destination_folder):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)
        print(f"Successfully extracted {file_path} to {destination_folder}")
    os.remove(file_path)
    print(f"Removed {file_path}")

url = "https://github.com/moonshadow565/ritobin/releases/download/2024-05-25-418af7a/ritobin.zip"
destination_folder = "../resources"

download_zip(url, destination_folder)

unzip_file(os.path.join(destination_folder, "ritobin.zip"), destination_folder)
