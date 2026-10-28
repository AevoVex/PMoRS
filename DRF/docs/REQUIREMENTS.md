# Соответствие заданиям DRF.pdf и DRF2.pdf

## Продолжение: DRF2.pdf — текущий Yatube

Источник: [DRF2.pdf](../../DRF2.pdf), 16 страниц. Эти требования заменяют формат итогового Yatube из первой части; прежние задания сохранены ниже с отметками выполнения и перенесены в учебный режим.

| Страницы | Требование | Реализация и проверка | Статус |
|---|---|---|---|
| 2 | Отдельное приложение api, вся текущая API-логика внутри | [api](../yatube/api), регистрация в INSTALLED_APPS | Выполнено |
| 2 | TokenAuthentication; только вошедшие; изменение только своего контента, иначе 403 | [permissions.py](../yatube/api/permissions.py), [settings.py](../yatube/yatube_api/settings.py); официальные и дополнительные тесты | Выполнено |
| 2–4 | Токен, CRUD постов, список и деталь групп, вложенный CRUD комментариев | [urls.py](../yatube/api/urls.py), 60 запросов Postman | Выполнено |
| 3 | Post через ModelViewSet | [PostViewSet](../yatube/api/views.py), наследование через AuthorContentViewSet | Выполнено |
| 3–4 | POST/PUT/PATCH возвращают объект; author=username, group=id | [сериализаторы](../yatube/api/serializers.py), тесты контрактов | Выполнено |
| 5, 15–16 | Общий надёжный get_post, родитель через 404, queryset через post.comments | [CommentViewSet](../yatube/api/views.py); проверки отсутствующего и неверного родителя | Выполнено |
| 6–11 | Коллекция Postman как вспомогательная проверка | [оригинальная коллекция](../yatube/postman_collection/CRUD_for_yatube.postman_collection.json), [результат CLI](postman-results.txt): 60 запросов, 88 assertions, 0 ошибок | Выполнено |
| 12–13 | Автотесты | [49 оригинальных тестов](../yatube/tests), без изменений проверок | Публичные тесты пройдены; платформа не запускалась |
| 13 | Все модели в админке | [admin.py](../yatube/posts/admin.py): Post, Group, Comment | Выполнено |
| 13–14 | Автор через специализированный RelatedField; не переопределять обычные поля | `SlugRelatedField(username)` только у author; поля группы и остальные поля берутся из моделей | Выполнено |
| 14 | URL разделён: api/ в проекте, v1/ в приложении, ресурсы в роутере | [yatube_api/urls.py](../yatube/yatube_api/urls.py), [api/urls.py](../yatube/api/urls.py) | Выполнено |
| 14–15 | Все контроллеры данных — вьюсеты; regex post_id через raw-строку с `\d+` | `router_v1`, вложенная регистрация comments | Выполнено |
| 15 | Группы read-only за счёт класса вьюсета | `GroupViewSet(ReadOnlyModelViewSet)`, даже staff не может писать через API | Выполнено |
| 15 | post комментария read-only через Meta | `CommentSerializer.Meta.read_only_fields` | Выполнено |
| 16 | Версия в имени роутера, явные basename, обратная связь comments | `router_v1`, basename у всех register, `post.comments` | Выполнено |

Существующая БД расширена миграцией `0002_comment`; очистка данных не применялась. Исходный скрипт коллекции с flush не запускался. Оригинальные тесты и коллекция получены из публичного api_yatube; происхождение и хеши — в [UPSTREAM.md](../yatube/UPSTREAM.md).

## Первая часть: DRF.pdf — сохранённые задания

Источник: [исходный PDF](../../DRF.pdf). Номера ниже — физические страницы PDF, начиная с 1. Текст просмотрен с сохранением границ страниц; страница 134 дополнительно проверена по изображению. Наборы тестов: [Yatube](../yatube/lessons/test_drf1.py), [Kittygram](../kittygram/cats/tests.py), [ранние уроки Kittygram](../kittygram/lessons/tests.py).

Методичка описывает последовательное развитие приложений. Например, отсутствие `id` в раннем сериализаторе и наличие `id` в позднем — разные этапы, а не одновременные требования. Финальное поведение определяется последними заданиями, ранние варианты сохранены в `lessons`.

## Yatube

| Страницы | Требование | Реализация и проверка | Статус |
|---|---|---|---|
| 29 | `ModelSerializer` для Post; `text`, `author`, `pub_date`; без `id` | [InitialPostSerializer](../yatube/lessons/serializers.py); `test_initial_serializer_excludes_id` | Выполнено, ранний этап |
| 50 | `api_posts`, GET списка и POST создания, `/api/v1/posts/` | [views.py](../yatube/lessons/function_views.py), [urls.py](../yatube/lessons/urls_functions.py); тесты создания и списка | Выполнено |
| 56–57 | Класс `APIPost(APIView)`, GET и POST | [lessons/views.py](../yatube/lessons/views.py), [urls_apiview.py](../yatube/lessons/urls_apiview.py); `test_apiview_lesson` | Выполнено, отдельный режим |
| 65 | `PostViewSet(ModelViewSet)` и роутер; все операции CRUD | [lessons/views.py](../yatube/lessons/views.py), [urls_viewset.py](../yatube/lessons/urls_viewset.py); `test_viewset_lesson_crud_and_permissions` | Выполнено, отдельный режим |
| 88–89 | Группа через slug; группа необязательна при создании/обновлении | [PostSerializer](../yatube/lessons/drf1_serializers.py); тест отсутствующей, неизвестной и очищенной группы | Выполнено |
| 102–103 | `character_quantity`: количество символов текста | `SerializerMethodField`, `len(obj.text)`; тесты списка, детали и пробелов | Выполнено |
| 134 | Обычный Token, доступ только после входа, endpoint `/api/v1/api-token-auth/` | [settings.py](../yatube/config/settings.py), функция `api_token_auth`; тесты входа и 401 | Выполнено |
| 134 | `author` только для чтения, автор из `request.user` | `read_only_fields`, `serializer.save(author=request.user)`; тест подмены автора | Выполнено |
| 134 | GET детали через `api_posts_detail`; изменять/удалять может только автор; иначе 403 | [views.py](../yatube/lessons/function_views.py); тест полного CRUD и запрета чужой записи | Выполнено |
| 89, 102, 134 | Поле `image` в составе модели/сериализатора | `ImageField`, multipart upload, тест реального PNG | Выполнено |

В учебном режиме DRF1 группа передаётся как `{"group": "cats"}`. В текущем DRF2 используется числовой ID: `{"group": 1}`. Это разные этапы задания, а не взаимозаменяемые форматы одного endpoint.

## Kittygram

| Страницы | Требование | Реализация и проверка | Статус |
|---|---|---|---|
| 30–37 | Простой Cat, GET/POST, исключение id, ответы 201/400/405 | [lessons/models.py](../kittygram/lessons/models.py), [serializers.py](../kittygram/lessons/serializers.py), `/functions/cats/`; тест начальной функции | Выполнено, ранний этап |
| 38–49 | View-функции, создание списка через `many=True`, CRUD, `partial=True` | `/functions/cats/`, `/bulk/cats/`; тесты функций, массового создания, ошибок и PATCH | Выполнено |
| 52–55 | APIView, затем ListCreateAPIView и RetrieveUpdateDestroyAPIView | [lessons/views.py](../kittygram/lessons/views.py); `/apiview/cats/`, `/generics/cats/`; тесты CRUD | Выполнено |
| 59–65 | ModelViewSet, роутер, корневой список ссылок | [финальный роутер](../kittygram/config/urls.py) и [учебный](../kittygram/lessons/urls.py) | Выполнено |
| 66–76 | Owner, связь один-ко-многим, `StringRelatedField`, обратные cats | [учебные модели](../kittygram/lessons/models.py), `/owners/`, `/cats/`; `test_owner_relations` | Выполнено, до версии 2 |
| 77–88 | Achievement, AchievementCat, many-to-many, вложенная запись, необязательные достижения | [cats/models.py](../kittygram/cats/models.py), [CatSerializer](../kittygram/cats/serializers.py); вложенное создание/обновление и пропуск поля | Выполнено, в итоговой модели |
| 90–91 | Вычисляемый возраст через SerializerMethodField | `get_age`; тест возраста; в раннем режиме неизвестный год даёт `null` | Выполнено |
| 92–97 | `Hex2NameColor`, webcolors, проверка hex; затем откат эксперимента | [lessons/serializers.py](../kittygram/lessons/serializers.py), `/hex-cats/`; тест named/unnamed/invalid hex | Выполнено, отдельный эксперимент |
| 97–99 | Переименование `name` достижения в `achievement_name` через source | [AchievementSerializer](../kittygram/cats/serializers.py); тест вложенного ввода/вывода | Выполнено |
| 99–101 | Ограничение цвета через choices | `CHOICES` и `ChoiceField`; тест недопустимого цвета | Выполнено |
| 108–110 | Дополнительный action: пять последних белых котов | `/cats/recent-white-cats/`, сортировка `-id`, лимит 5; тест точного порядка | Выполнено |
| 110–112 | Отдельный сериализатор списка, только id/name/color | `CatListSerializer`, `get_serializer_class`; тест формы списка/детали | Выполнено |
| 113–117 | CreateRetrieveViewSet из миксинов, LightCatViewSet, `/mycats/` | [views.py](../kittygram/cats/views.py); POST и GET детали разрешены, остальные действия 405 | Выполнено |
| 118–119 | Низкоуровневый ViewSet с list/retrieve | [ReadOnlyCatViewSet](../kittygram/lessons/views.py), `/readonly-cats/`; тест чтения и 405 | Выполнено, отдельный пример |
| 121–124 | Промежуточная TokenAuthentication, IsAuthenticated, получение токена | [lesson_settings.py](../kittygram/config/lesson_settings.py), `KITTYGRAM_LESSON_TOKEN=1`, `/api-token-auth/` | Выполнено, отдельный режим |
| 127–133 | Djoser + SimpleJWT; регистрация, создание/обновление JWT, Bearer | [settings.py](../kittygram/config/settings.py), `/auth/users/`, `/auth/jwt/*/`; тест полного цикла | Выполнено |
| 135–138 | Вместо Owner — встроенный User; пользователи read-only, достижения и коты через вьюсеты | [модели](../kittygram/cats/models.py), [вьюсеты](../kittygram/cats/views.py); тест пользователей | Выполнено |
| 135, 139–142 | Владельца нельзя подменить; owner из request; только хозяин меняет кота | `IsOwnerOrReadOnly`, `perform_create`; тесты подмены и 403 | Выполнено |
| 143–146 | Валидаторы года рождения и несовпадения имени с цветом | `validate_birth_year`, `validate`; границы возраста и PATCH проверены | Выполнено |
| 147–152 | Уникальная пара name/owner в БД и сериализаторе; CurrentUserDefault | `UniqueConstraint`, `UniqueTogetherValidator`, read-only owner с default; тесты создания, переименования, ограничения БД | Выполнено |

Из двух альтернатив на страницах 151–152 выбран `PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())`, поэтому owner виден в ответе. Одновременно применять HiddenField не требуется.

## Что не является отдельным заданием

Страницы 1–28 — теория REST, примеры HTTP-клиентов, внешних API и сериализации; 104–107 — объяснение регулярных выражений. Примеры Book и hello иллюстрируют понятия, но не являются отдельными Yatube/Kittygram-продуктами. Их механизмы применены в двух проектах. Возможные комментарии к котам на странице 63 — гипотетический пример `get_queryset`, а не требование создать комментарии.

Ссылки на три исходных репозитория Kittygram найдены в аннотациях PDF; README всех трёх просмотрены, финальные модели/сериализаторы/вьюсеты сопоставлены с исходником. Здесь подготовлена самостоятельная локальная реализация итогового задания, а не три копии старых репозиториев. [Источники и различия](REPORT.md#источники).

При выполнении первой части исходных тестов в папке не было. Для продолжения получен публичный официальный набор api_yatube и его чек-лист. Закрытая проверка на учебной платформе и сдача работы не выполнялись.
