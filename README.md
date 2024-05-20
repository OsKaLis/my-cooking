<div id="header" align="center">
  <h1>Проект my-cooking.ru</h1>
</div>

## Что это за проект, какую задачу он решает, в чём его польза;
> [!NOTE]
> my-cooking.ru сайт, на котором пользователи будут публиковать рецепты,
> добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
> Пользователям сайта также будет доступен сервис «Список покупок».
> Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Реализованно роли и прав доступа:
### Анонимные пользователи:
* [1] Создать аккаунт.
* [2] Просматривать рецепты на главной.
* [3] Просматривать отдельные страницы рецептов.
* [4] Просматривать страницы пользователей.
* [5] Фильтровать рецепты по тегам.
### Авторизованные пользователи:
* [1] Входить/выходить в систему под своим логином и паролем.
* [2] Менять свой пароль.
* [3] Создавать/редактировать/удалять собственные рецепты
* [4] Просматривать рецепты на главной, страницы пользователей, отдельные страницы рецептов
* [5] Фильтровать рецепты по тегам.
* [6] Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
* [7] Работать с персональным списком покупок: добавлять/удалять **любые** рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
* [8] Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.
### Администратор:
* [1] обладает правами авторизованного пользователя
* [2] изменять пароль любого пользователя,
* [3] редактировать/удалять **любые** рецепты,
* [4] добавлять/удалять/редактировать ингредиенты.
* [5] добавлять/удалять/редактировать теги.

## Как развернуть проект на локальной машине.
> [!IMPORTANT]
> * [1] (Клонируем проект) :git clone git@github.com:OsKaLis/my-cooking.git
> * [2] (водим пароль если доступ приватный)
> * [3] (Переходим в директорию проекта) :cd my-cooking/
> * [4] (Создание файла с настройками ".env"):
>   ```
>   POSTGRES_DB=[{Своё значение название базы}]
>   POSTGRES_USER=[{Своё значение имя пользователя для подключения к базе}]
>   POSTGRES_PASSWORD=[{Своё значение пароля для базы}]
>   DB_NAME=[{Своё значение название базы}]
>   Добавляем переменные для Django-проекта:
>   DB_HOST=db
>   DB_PORT=5432
>   SECRET_KEY=[{Своё значение key}]
>   DEBUG=False
> * [5] (Установка docker для Windows) https://learn.microsoft.com/ru-ru/windows/wsl/install
> * [6] (Установка docker для Linux):
>   ``` 
>   [1] sudo apt update
>   [2] sudo apt install curl
>   [3] curl -fSL https://get.docker.com -o get-docker.sh 
>   [4] sudo sh ./get-docker.sh
>   [5] sudo apt-get install docker-compose-plugin
>   [6] sudo systemctl status docker 
>   systemctl — программа, контролирующая работу системных демонов
>   status docker — команда, проверяющая статус демона Docker
> * [7] (Запуск проекта)
>   ```
>   [1] (Запускаем основные контейнеры): sudo docker compose up -d
>   [2] (Выполняет миграции и сбор статики):
>   [3] sudo docker compose exec backend python manage.py migrate
>   [4] sudo docker compose exec backend python manage.py collectstatic
>   [5] sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
> * [8] (Главная адрес проекта): http://127.0.0.1:8000/
> * [9] (API адрес проекта) :http://127.0.0.1:8000/api/
> * [10] (Админка проекта) :http://127.0.0.1:8000/admin/

## Cтек технологий:
<img src="https://img.shields.io/badge/PostgreSQL_-13.12-white"> <img src="https://img.shields.io/badge/Python_-3.9.10-green"> <img src="https://img.shields.io/badge/Gunicorn_-20.1.0-black">
<img src="https://img.shields.io/badge/Django_-3.2.3-green"> <img src="https://img.shields.io/badge/Rest_-3.12.4-deepskyblue"> <img src="https://img.shields.io/badge/Docker_-24.0.5-blue">
<img src="https://img.shields.io/badge/Nginx_-1.19.3-green"> 

## Некоторые примеры индпоинтов.
### Список пользователей, регистрация нового пользователя, метод: [GET], [POST]
```
https://my-cooking.ru/api/users/
```
### Профиль пользователя и собственный профиль пользователя, метод: [GET]
```
https://my-cooking.ru/api/users/{id}/     
https://my-cooking.ru/api/users/me/     
```
### Изменение пароля пользователя, метод: [POST]
```
https://my-cooking.ru/api/users/set_password/     
```
### Получение и удаление токена авторизации, метод: [POST]
```
https://my-cooking.ru/api/auth/token/login/
https://my-cooking.ru/api/auth/token/logout/
```
### Получение, создание рецептов, их обновление и удаление
методы: [GET], [POST]
```
https://my-cooking.ru/api/recipes/   
```
### метод: [GET], [PATCH], [DEL]
```
https://my-cooking.ru/api/recipes/{id}/   
```
### Добавление понравившегося рецепта в "Избранное" и удаление его, методы: [POST], [DELETE]
```
https://my-cooking.ru/api/recipes/{id}/favorite/    
```
### Добавление рецепта в "Список покупок" и удаление его из списка, методы: [POST], [DELETE]
```
https://my-cooking.ru/api/recipes/{id}/shopping_cart/    
```
### Скачивание файла в формате PDF с ингредиентами рецептов из списка покупок, метод: [GET]
```
https://my-cooking.ru/api/recipes/download_shopping_cart/     
```
### Просмотр доступных тегов, метод: [GET]
```
https://my-cooking.ru/api/tags/     
https://my-cooking.ru/api/tags/{id}     
```
### Просмотр доступных ингредиентов, метод: [GET]
```
https://my-cooking.ru/api/ingredients/     
https://my-cooking.ru/api/ingredients/{id}/    
```
## Автор: Юшко Ю.Ю.
