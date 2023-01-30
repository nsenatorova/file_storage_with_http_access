### Хранилище файлов с доступом по http

Реализованы загрузка, скачивание и удаление файлов. 

Так как регистрация новых пользователей не предусмотрена, для авторизации введено два пользователя:
1. логин first_user, пароль first_password
2. логин second_user, пароль second_password

Для скачивания и удаления файлов хэш передается в json-е:
```
{'hash_name': name}
```
Примеры запросов к сервису находятся в test.py