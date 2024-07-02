import requests
import os
import zipfile
import logging
import os
import requests
import shutil

def download_folder(dest_folder):
    try:
        download_url = 'http://localhost:4000/launcher/download/downloadAssembly'
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        zip_path = os.path.join(dest_folder, 'game.zip')
        print(zip_path)
        logging.info(f'Saving ZIP archive to: {zip_path}')

        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logging.info('ZIP archive saved successfully.')

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)

        logging.info('ZIP archive extracted successfully.')

        os.remove(zip_path)
        logging.info('ZIP archive deleted after extraction.')

    except requests.exceptions.RequestException as e:
        logging.error(f'Failed to download folder: {e}')
        return False
    except Exception as e:
        logging.error(f'Error during download or extraction: {e}')
        return False

def checkUpdateModpack(current_version):
    try:
        url = 'http://localhost:4000/launcher/update/checkUpdateAssembly'
        params = {'version': current_version}
        response = requests.get(url, params=params)
        response.raise_for_status()

        update_info = response.json()
        return update_info
    except requests.exceptions.RequestException as e:
        print(f'Failed to check for updates: {e}')
        return False
    
def checkUpdateLauncher(current_version):
    try:
        url = 'http://localhost:4000/launcher/update/checkUpdateLauncher'
        params = {'version': current_version}
        response = requests.get(url, params=params)
        response.raise_for_status()

        update_info = response.json()
        return update_info
    except requests.exceptions.RequestException as e:
        print(f'Failed to check for updates: {e}')
        return False

def downloadUpdateModpack(dest_folder, updateInfo):
    try:
        url = 'http://localhost:4000/launcher/update/downloadUpdateAssembly'
        response = requests.get(url, stream=True)
        response.raise_for_status() 

        zip_path = os.path.join(dest_folder, 'game.zip')

        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


        print('Update downloaded and applied successfully.')

        # Проверяем и удаляем старые папки, если они указаны в updateInfo
        folders_to_delete = updateInfo
        for folder in folders_to_delete:
            folder_path = os.path.join(dest_folder, folder)
            if os.path.exists(folder_path):
                try:
                    if os.path.isfile(folder_path):
                        os.remove(folder_path)
                        print(f'Deleted old file: {folder}')
                    elif os.path.isdir(folder_path):
                        shutil.rmtree(folder_path)
                        print(f'Deleted old folder: {folder}')
                except OSError as e:
                    print(f'Failed to delete {folder}: {e}')

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)

        os.remove(zip_path)
        return True
    except requests.exceptions.RequestException as e:
        print(f'Failed to download update: {e}')
        return False
    except Exception as e:
        print(f'Error during update process: {e}')
        return False
    
def downloadUpdateLauncher(dest_folder, updateInfo):
    try:
        url = 'http://localhost:4000/launcher/update/downloadUpdateAssembly'
        response = requests.get(url, stream=True)
        response.raise_for_status() 
        
        zip_path = os.path.join(dest_folder, 'launcher.zip')

        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


        print('Update downloaded and applied successfully.')

        # Проверяем и удаляем старые папки, если они указаны в updateInfo
        folders_to_delete = updateInfo
        for folder in folders_to_delete:
            folder_path = os.path.join(dest_folder, folder)
            if os.path.exists(folder_path):
                try:
                    if os.path.isfile(folder_path):
                        os.remove(folder_path)
                        print(f'Deleted old file: {folder}')
                    elif os.path.isdir(folder_path):
                        shutil.rmtree(folder_path)
                        print(f'Deleted old folder: {folder}')
                except OSError as e:
                    print(f'Failed to delete {folder}: {e}')

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)

        os.remove(zip_path)
        return True
    except requests.exceptions.RequestException as e:
        print(f'Failed to download update: {e}')
        return False
    except Exception as e:
        print(f'Error during update process: {e}')
        return False