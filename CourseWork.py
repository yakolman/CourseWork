import json
import requests
import tqdm
import yaml

# class ConfigLoader:
#     def __init__ (self, config_path='config.yaml'):
#         self.config_path = config_path
#
#     def load_config(self):
#         try:
#             with open (self.config_path, 'r', encoding = 'utf-8') as f:
#                 ya_token = yaml.safe_load(f)
#                 return ya_token['yandex_token']['token']
#         except (TypeError):
#             raise Exception ('Не верный тип данных')
#         except (KeyError):
#             raise Exception ('Не верно задан ключ')
#         except (FileNotFoundError):
#             raise Exception ('Config файл с токеном не найден')

class DogApi:
    def __init__ (self):
        self.base_url= 'https://dog.ceo/api'

    def get_subbreeds (self, breed):
        url_subbreed = f'{self.base_url}/breed/{breed}/list'
        response = requests.get (url_subbreed)
        return response.json()['message']

    def get_images(self, breed, subbreed = None):
        if subbreed:
            url = f'{self.base_url}/breed/{breed}/{subbreed}/images/random'
        else:
            url = f'{self.base_url}/breed/{breed}/images'
        response = requests.get(url)
        img_list = response.json()
        return img_list['message']

class YndDiskUploader:
    def __init__(self,token):
        self.token = token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {
            'Authorization': token
        }

    def create_folder (self, folder_name):
        params = {
            'path': folder_name
        }
        requests.put(self.base_url, params=params, headers=self.headers)

    def upload_file(self, image_url, folder_name_breed, filename):
        params = {
            'path': f'{folder_name_breed}/{filename}',
            'url': image_url
        }
        url = f'{self.base_url}/upload'
        requests.post(url, params=params, headers=self.headers).json()

def main():
    #Пользовательский ввод
    breed = input ('Введите породу собаки: ').strip().lower()
    ya_token = input('Введите токен яндекс диска: ')
    token = f'OAuth {ya_token}'
    #Инициализация API
    dog_api = DogApi()
    uploader = YndDiskUploader(token)
    #Создание папки на Яндекс диске с именем породы
    uploader.create_folder(breed)
    #Проверка подпород у породы:
    subbreeds = dog_api.get_subbreeds(breed)
    results = []

    if subbreeds: #Если подпорода есть
        for subbreed in tqdm.tqdm(subbreeds, desc ='Загрузка изображений'):
            image_url = dog_api.get_images(breed, subbreed)
            filename = f"{breed}_{subbreed}_{image_url.split('/')[-1]}"
            uploader.upload_file(image_url, breed, filename)
            results.append({'file_name': filename})
    else: #Подпород нет
        image_urls = dog_api.get_images(breed)
        for image_url in tqdm.tqdm(image_urls, desc='Загрузка изображений для'):
            filename = f"{breed}_{image_url.split('/')[-1]}"
            uploader.upload_file(image_url, breed, filename)
            results.append({"file_name": filename})

    #Логирование в Json
    with open ('result.json', 'w') as f:
        json.dump(results, f, indent = 2)

if __name__ == '__main__':
    main()