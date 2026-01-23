# Telegram Subscription Checker Bot

[Русский](#russian) | [English](#english)

<a name="russian"></a>
## 🇷🇺 Telegram Subscription Checker Bot

Бот для администрирования групповых чатов, который обеспечивает принудительную подписку участников чата на определенные каналы. Проект предназначен для личного использования владельцами групп и каналов (Self-hosted).

### Особенности

*   **Zero Configuration**: Автоматическая регистрация каналов при добавлении бота администратором.
*   **Производительность**: Использует Redis для кэширования статусов подписки (снижение нагрузки на Telegram API).
*   **Надежность**:
    *   `RetryMiddleware` для повторных запросов при сетевых сбоях.
    *   Автоматические миграции базы данных при запуске.
    *   Docker Healthchecks для корректного запуска зависимостей.
*   **Стек**: Python 3.13, Aiogram 3.24, SQLAlchemy (Async), PostgreSQL, Redis, Docker.

---

### 📂 Структура проекта

```text
.
├── .dockerignore           # Файлы, игнорируемые при сборке Docker
├── .env.example            # Пример файла конфигурации окружения
├── .gitignore              # Файлы, игнорируемые Git
├── .python-version         # Версия Python для проекта
├── alembic.ini             # Конфигурация Alembic для миграций
├── docker-compose.yml      # Оркестрация (Bot + Postgres + Redis + Migration Service)
├── Dockerfile              # Multi-stage сборка
├── pyproject.toml          # Зависимости (uv)
├── README.md               # Документация проекта
├── uv.lock                 # Lock-файл зависимостей uv
├── alembic/                # Миграции БД
│   ├── env.py              # Окружение Alembic
│   ├── README              # Документация по миграциям
│   ├── script.py.mako      # Шаблон скрипта миграции
│   └── versions/           # Версии миграций
│       └── ba051ae155a4_try_migate.py  # Пример миграции
└── app/                    # Основное приложение
    ├── __init__.py         # Инициализация модуля
    ├── config.py           # Конфигурация (Pydantic)
    ├── container.py        # DI Контейнер
    ├── logging.py          # Конфигурация логирования
    ├── main.py             # Точка входа
    ├── bot/                # Telegram слой (Handlers, Middlewares)
    │   ├── __init__.py     # Инициализация модуля
    │   ├── keyboards/      # Клавиатуры бота
    │   │   ├── __init__.py # Инициализация модуля
    │   │   └── subscription.py  # Клавиатура подписки
    │   ├── middlewares/    # Middleware бота
    │   │   ├── __init__.py # Инициализация модуля
    │   │   ├── container.py  # DI контейнер для middleware
    │   │   ├── request.py  # Обработка запросов
    │   │   └── subscription.py  # Middleware проверки подписки
    │   └── routers/        # Роутеры бота
    │       ├── __init__.py # Инициализация модуля
    │       └── admin.py    # Админ команды
    ├── models/             # SQLAlchemy модели
    │   ├── __init__.py     # Инициализация модуля
    │   └── channel.py      # Модель канала
    ├── services/           # Бизнес-логика
    │   ├── __init__.py     # Инициализация модуля
    │   └── subscription.py # Сервис управления подписками
    └── storage/            # Слой данных
        ├── __init__.py     # Инициализация модуля
        └── repositories/   # Репозитории
            ├── __init__.py # Инициализация модуля
            └── channels.py # Репозиторий каналов
```

---

### 🚀 Установка и запуск

#### Вариант 1: Docker Compose (Рекомендуемый)

1.  **Клонируйте репозиторий**:
    ```bash
    git clone <repository-url>
    cd TelegramSubscriptionBot
    ```

2.  **Настройка окружения**:
    Скопируйте пример конфига и вставьте свой токен бота и параметры БД:
    ```bash
    cp .env.example .env
    nano .env
    # Установите BOT_TOKEN=...
    # Настройте POSTGRES_USER, POSTGRES_PASSWORD и др.
    ```

3.  **Запуск**:
    ```bash
    docker compose up --build -d
    ```
    *Бот автоматически применит миграции и запустится, как только база данных будет готова.*

#### Вариант 2: Локальный запуск (для разработки)

Требуется установленный `uv` (администратор пакетов Python).

1.  **Запуск зависимостей**:
    ```bash
    docker compose up -d postgres redis
    ```

2.  **Установка зависимостей**:
    ```bash
    uv sync
    ```

3.  **Применение миграций**:
    ```bash
    uv run alembic upgrade head
    ```

4.  **Запуск бота**:
    ```bash
    uv run python -m app.main
    ```

---

### 🛠 Использование

1.  **Добавление канала**: Добавьте бота в свой канал как администратора. Бот автоматически сохранит канал в базу данных.
2.  **Проверка подписки**: Добавьте бота в свою группу как администратора.
3.  **Проверка**: Если пользователь напишет в группу, не подписавшись на ваш канал, бот удалит сообщение и покажет кнопку для подписки.

**Команды администратора**:
*   `/channels` — Показать список охраняемых каналов.

**Отключение проверок**:
Чтобы бот перестал требовать подписку, выполните одно из действий:
1.  Удалите бота из администраторов канала (он автоматически удалит канал из базы).
2.  Удалите бота из администраторов группы.

---

<a name="english"></a>
## 🇺🇸 Telegram Subscription Checker Bot

A group chat administration bot that enforces mandatory channel subscriptions for chat members. Designed for self-hosted use by group/channel owners.

### Features

*   **Zero Configuration**: Automatically registers channels when the bot is promoted to admin.
*   **Performance**: Redis caching for subscription status (reduces Telegram API calls).
*   **Reliability**:
    *   `RetryMiddleware` handles network instability.
    *   Automatic database migrations on startup.
    *   Docker Healthchecks ensure proper startup order.
*   **Tech Stack**: Python 3.13, Aiogram 3.24, SQLAlchemy (Async), PostgreSQL, Redis, Docker.

---

### 📂 Project Structure

```text
.
├── .dockerignore           # Files ignored during Docker build
├── .env.example            # Environment configuration example
├── .gitignore              # Files ignored by Git
├── .python-version         # Python version for the project
├── alembic.ini             # Alembic configuration for migrations
├── docker-compose.yml      # Orchestration (Bot + Postgres + Redis + Migration Service)
├── Dockerfile              # Multi-stage build
├── pyproject.toml          # Dependencies (uv)
├── README.md               # Project documentation
├── uv.lock                 # Dependency lock file for uv
├── alembic/                # DB Migrations
│   ├── env.py              # Alembic environment
│   ├── README              # Migration documentation
│   ├── script.py.mako      # Migration script template
│   └── versions/           # Migration versions
│       └── ba051ae155a4_try_migate.py  # Sample migration
└── app/                    # Main application
    ├── __init__.py         # Module initialization
    ├── config.py           # Configuration (Pydantic)
    ├── container.py        # DI Container
    ├── logging.py          # Logging configuration
    ├── main.py             # Entry point
    ├── bot/                # Telegram layer (Handlers, Middlewares)
    │   ├── __init__.py     # Module initialization
    │   ├── keyboards/      # Bot keyboards
    │   │   ├── __init__.py # Module initialization
    │   │   └── subscription.py  # Subscription keyboard
    │   ├── middlewares/    # Bot middlewares
    │   │   ├── __init__.py # Module initialization
    │   │   ├── container.py  # DI container for middleware
    │   │   ├── request.py  # Request processing
    │   │   └── subscription.py  # Subscription check middleware
    │   └── routers/        # Bot routers
    │       ├── __init__.py # Module initialization
    │       └── admin.py    # Admin commands
    ├── models/             # SQLAlchemy models
    │   ├── __init__.py     # Module initialization
    │   └── channel.py      # Channel model
    ├── services/           # Business logic
    │   ├── __init__.py     # Module initialization
    │   └── subscription.py # Subscription management service
    └── storage/            # Data layer
        ├── __init__.py     # Module initialization
        └── repositories/   # Repositories
            ├── __init__.py # Module initialization
            └── channels.py # Channels repository
```

---

### 🚀 Installation & Run

#### Option 1: Docker Compose (Recommended)

1.  **Clone repository**:
    ```bash
    git clone <repository-url>
    cd TelegramSubscriptionBot
    ```

2.  **Environment Setup**:
    Copy the example config and set your bot token and database credentials:
    ```bash
    cp .env.example .env
    nano .env
    # Set BOT_TOKEN=...
    # Configure POSTGRES_USER, POSTGRES_PASSWORD, etc.
    ```

3.  **Run**:
    ```bash
    docker compose up --build -d
    ```
    *The bot will automatically apply migrations and start once the database is healthy.*

#### Option 2: Local Run (Development)

Requires `uv` (Python package manager).

1.  **Start dependencies**:
    ```bash
    docker compose up -d postgres redis
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Apply migrations**:
    ```bash
    uv run alembic upgrade head
    ```

4.  **Start bot**:
    ```bash
    uv run python -m app.main
    ```

---

### 🛠 Usage

1.  **Add Channel**: Add the bot to your channel as an Administrator. It will automatically be saved to the database.
2.  **Protect Group**: Add the bot to your group as an Administrator.
3.  **Enforcement**: If a user posts in the group without subscribing to your channel, the bot deletes the message and prompts them to subscribe.

**Admin Commands**:
*   `/channels` — List protected channels.

**Disabling Checks**:
To stop subscription enforcement, do one of the following:
1.  Remove the bot from the channel administrators (auto-removes from DB).
2.  Remove the bot from the group administrators.
