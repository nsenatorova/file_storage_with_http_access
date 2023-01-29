import requests

URL_UPLOAD = 'http://127.0.0.1:5000/upload'
URL_DOWNLOAD = 'http://127.0.0.1:5000/download'
URL_DELETE = 'http://127.0.0.1:5000/delete'

files = {'file': open('test_image.jpg', 'rb')}
response_upload = requests.post(URL_UPLOAD, files=files, auth=('first_user', 'first_password'), timeout=10)
print(response_upload.text)

jsn = {'hash_name': response_upload.text.split()[3][:-1]}

response_download = requests.post(url=URL_DOWNLOAD, json=jsn, timeout=10)
if response_download.status_code == 200:
    with open("downloaded_image.jpg", 'wb') as f:
        f.write(response_download.content)

response_delete = requests.post(url=URL_DELETE, json=jsn, auth=('first_user', 'first_password'), timeout=10)
print(response_delete.text)
