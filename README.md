# Сайт курсов разработан на Flask

Использовала:
Все, что использовала, есть в [requirements.txt](requirements.txt)

Функционал:
- домашняя страница с описанием
- регистрация и login / logout пользователей,
- раздел курсов, гле показаны все курсы сайта с обозначением категорий.
При нажатии на заголовок курса можно почитать его полное описание. При нажатии на кнопку "Начать", по которой просмотреть сам курс может только авторизованный пользователь 
- раздел мои курсы только для авторизованных пользователей. Пользователь видит все начатые им курсы и может открыть их
- на странице администратора можно добавлять, изменять и удалять пользователей и курсы. Вход по логину, паролю определенных пользователей

Все настройки находятся в [app.py](app.py)