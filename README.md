**Задание**



upd 14.05.23 0:36 ЧТО ВО ФРОНТЕ НЕ ДОДЕЛАНО, ОСТАВЛЯЕМ КАК ЕСТЬ
1. Не реализована обработка результатов оформления заказа.
см. отсутствие хука mounted() в payment, отсутствие обработки результатов /api/payment...
2. Не реализована отправка на бэкенд введённого нового пароля - profile.js, метод changePassword - 
запрос на бэкенд о смене пароля выглядит как this.postData('/api/profile/password/') - Без передачи нового пароля






------- ДОДЕЛАНО ПО ФРОНТЕНДУ
1. Описание продукта в корзине - не было реализовано
2. В файле order-details.js фронтенд лазил на бэк по ссылке, неверно отражённой в сваггере.
Было /order/{order_id}, а в сваггере и в других скриптах js - на /orders/{order_id}