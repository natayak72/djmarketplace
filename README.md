**Задание**

<hr>

**Структура сайта**
1. Главная страница
2. Каталог с фильтром и сортировкой
    2.1 Сам каталог товаров
        2.1.1 ~~Отображение списка товаров с сортировкой~~
        2.1.2 Фильтрация товаров
    2.2 ~~Детальная страница товара, со~~ ~~списком отзывов~~ и тегами
    2.3 ~~Создать новый отзыв на детальной странице товара~~
3. Оформление заказа
    3.1 Корзина
    3.2 Оформление заказа
    3.3 Оплата
4. Личный кабинет
    4.1 Личный кабинет
    4.2 Профиль
    4.3 История заказов
5. ~~Админка~~


<hr>

**Роли на сайте**

1. Администратор - полный доступ к админке
2. Покупатель - любой авторизованный пользователь, может пользоваться
 всеми публичными возможностями системы
3. Незарегистрированный пользователь - может просматривать каталоги
 и собирать корзину

Порядок запуска:
1. python manage.py migrate
2. python createsuperuser
3. заходим в админку, создаём товары (Products) и магазины (Shops)
4. В админке в разделе Product in Shops выбираем, какие товары в каких магазинах в каком количестве будут продаваться
4. Можно регистрироваться, покупать товары, пополнять счёт и т.п.

----------- ВОПРОСЫ
1. Главная страница. Топ-товаров.   
"В каталог топ-товаров попадают 8 первых товаров 
по параметру "индекс сортировки". Если индекс совпадает, то по количеству
покупок." Что такое индекс сортировки? 
2. ПОКУПКА ТОВАРА - не появляется всплывающее уведомление с возможностью
перейти в корзину или продолжить покупки.
3. НЕВЕРНО ЗАПОЛНЕННЫЕ ПОЛЯ ОТЗЫВА
Если ввести, например, невалидный email, то на фронте это никак не отобразится.
Метод submitReview() файла product-detail.js не имеет в себе механизмов обработки ошибок.
4. ТЕГИ. Что такое теги? Либо пролистал ТЗ по диагонали, либо не нашёл.