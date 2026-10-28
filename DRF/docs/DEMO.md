# Как показать работу и объяснить решение

Сначала запустите оба сервера по [README](../README.md). Команды ниже выполняйте в третьем терминале PowerShell. В демобазах уже есть alice и bob с паролем `Demo-Learning-42!`. Если вы запускали `seed_demo` с другим паролем, подставьте его.

## 1. Yatube: авторизация и публикация

```powershell
$yatube = 'http://127.0.0.1:8000'
$login = @{ username = 'alice'; password = 'Demo-Learning-42!' } | ConvertTo-Json
$token = Invoke-RestMethod "$yatube/api/v1/api-token-auth/" -Method Post -ContentType 'application/json' -Body $login
$headers = @{ Authorization = "Token $($token.token)" }
Invoke-RestMethod "$yatube/api/v1/groups/" -Headers $headers
$body = @{ text = 'Hello, Yatube!'; group = 'cats' } | ConvertTo-Json
$post = Invoke-RestMethod "$yatube/api/v1/posts/" -Method Post -Headers $headers -ContentType 'application/json' -Body $body
$post | ConvertTo-Json -Depth 5
```

В ответе автор назначен автоматически, группа возвращена slug, число символов равно 14. Поля id и дата сформированы сервером.

```powershell
$patch = @{ text = 'Updated post' } | ConvertTo-Json
Invoke-RestMethod "$yatube/api/v1/posts/$($post.id)/" -Method Patch -Headers $headers -ContentType 'application/json' -Body $patch
```

Ожидаются новый текст и `character_quantity: 12`. PATCH принимает только изменяемое поле.

Вход второго пользователя и проверка защиты:

```powershell
$bobLogin = @{ username = 'bob'; password = 'Demo-Learning-42!' } | ConvertTo-Json
$bobToken = Invoke-RestMethod "$yatube/api/v1/api-token-auth/" -Method Post -ContentType 'application/json' -Body $bobLogin
$bobHeaders = @{ Authorization = "Token $($bobToken.token)" }
try {
    Invoke-RestMethod "$yatube/api/v1/posts/$($post.id)/" -Method Delete -Headers $bobHeaders
} catch {
    [int]$_.Exception.Response.StatusCode
}
```

Должно появиться `403`. Теперь автор может удалить свою запись:

```powershell
Invoke-RestMethod "$yatube/api/v1/posts/$($post.id)/" -Method Delete -Headers $headers
```

Успешный ответ пустой, статус 204.

## 2. Kittygram: JWT, кот и достижения

```powershell
$kittygram = 'http://127.0.0.1:8001'
$jwt = Invoke-RestMethod "$kittygram/auth/jwt/create/" -Method Post -ContentType 'application/json' -Body $login
$catHeaders = @{ Authorization = "Bearer $($jwt.access)" }
$catName = 'Demo' + (Get-Random -Minimum 10000 -Maximum 99999)
$body = @{
    name = $catName
    color = 'White'
    birth_year = (Get-Date).Year - 2
    achievements = @(@{ achievement_name = 'Knocked over a tree' })
} | ConvertTo-Json -Depth 5
$cat = Invoke-RestMethod "$kittygram/cats/" -Method Post -Headers $catHeaders -ContentType 'application/json' -Body $body
$cat | ConvertTo-Json -Depth 5
Invoke-RestMethod "$kittygram/cats/" -Headers $catHeaders
Invoke-RestMethod "$kittygram/cats/$($cat.id)/" -Headers $catHeaders
Invoke-RestMethod "$kittygram/cats/recent-white-cats/" -Headers $catHeaders
```

Покажите разницу: список короткий, деталь содержит age=2, owner и вложенный список достижений. Поля owner и age не понадобились в запросе.

```powershell
$body = @{ achievements = @() } | ConvertTo-Json
Invoke-RestMethod "$kittygram/cats/$($cat.id)/" -Method Patch -Headers $catHeaders -ContentType 'application/json' -Body $body
$refreshBody = @{ refresh = $jwt.refresh } | ConvertTo-Json
$refreshed = Invoke-RestMethod "$kittygram/auth/jwt/refresh/" -Method Post -ContentType 'application/json' -Body $refreshBody
$catHeaders = @{ Authorization = "Bearer $($refreshed.access)" }
Invoke-RestMethod "$kittygram/cats/$($cat.id)/" -Method Delete -Headers $catHeaders
```

Массив достижений очищается, новый access работает, запись удаляется своим владельцем. Очистка связи не удаляет общее достижение из справочника.

## 3. Что проверить на ошибки

В Postman отправьте запросы по [готовым примерам](../requests/kittygram.http):

- GET `/cats/` без Authorization → 401.
- POST кота с будущим годом → 400 в birth_year.
- POST кота с цветом `Purple` → 400 в color.
- POST с name=`White`, color=`White` → 400.
- Дважды создать одно имя под одним владельцем → второй ответ 400.
- Получить JWT bob и изменить кота alice → 403.
- GET `/mycats/` с действующим токеном → 405; POST туда разрешён.

Для Postman задавайте Body → raw → JSON и `Content-Type: application/json`. У Yatube заголовок содержит **Token**, у Kittygram — **Bearer**. Для загрузки изображения Yatube выберите Body → form-data: `text` как Text, `image` как File. Не задавайте boundary вручную: Postman установит его сам.

В [requests](../requests) лежат `.http`-файлы для расширения REST Client в VS Code. В них нужно вручную вставить полученные токены и актуальные id в переменные вверху. Это шаблоны запросов, реальные токены в файлах не сохранены.

## Что сказать на защите

«Я сделал два REST API на Django REST Framework. Модели описывают данные и связи, сериализаторы превращают модели в JSON и валидируют вход, представления обрабатывают HTTP-запросы. В Yatube оставил функции, потому что так требует последнее задание, в Kittygram применил вьюсеты. Автор и владелец определяются по токену, поэтому их нельзя подменить телом запроса. Ограничения проверяются и в сериализаторе, и, для уникальности, в базе. Ранние варианты сохранил отдельно, чтобы показать переход от функций к классам и вьюсетам. Работу проверил автоматическими тестами и реальными HTTP-запросами».

Для подробных вопросов используйте [архитектуру](ARCHITECTURE.md), [отчёт](REPORT.md) и [таблицу требований](REQUIREMENTS.md).
