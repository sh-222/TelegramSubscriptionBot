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
    *   `entrypoint.sh` для автоматических миграций при старте.
    *   Docker Healthchecks для корректного запуска зависимостей.
*   **Стек**: Python 3.13, Aiogram 3.24, SQLAlchemy (Async), PostgreSQL, Redis, Docker.

---

### 📂 Структура проекта

```text
.
├── app/
│   ├── bot/                # Telegram слой (Handlers, Middlewares)
│   ├── services/           # Бизнес-логика (SubscriptionService)
│   ├── storage/            # Слой данных (Repositories, Engine)
│   ├── models/             # SQLAlchemy модели
│   ├── config.py           # Конфигурация (Pydantic)
│   ├── container.py        # DI Контейнер
│   └── main.py             # Точка входа
├── alembic/                # Миграции БД
├── entrypoint.sh           # Скрипт запуска (Migarations + App)
├── Dockerfile              # Multi-stage сборка
├── docker-compose.yml      # Оркестрация (Bot + Postgres + Redis)
└── pyproject.toml          # Зависимости (uv)
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
---

<a name="english"></a>
## 🇺🇸 Telegram Subscription Checker Bot

A group chat administration bot that enforces mandatory channel subscriptions for chat members. Designed for self-hosted use by group/channel owners.

### Features

*   **Zero Configuration**: Automatically registers channels when the bot is promoted to admin.
*   **Performance**: Redis caching for subscription status (reduces Telegram API calls).
*   **Reliability**:
    *   `RetryMiddleware` handles network instability.
    *   `entrypoint.sh` runs migrations automatically on startup.
    *   Docker Healthchecks ensure proper startup order.
*   **Tech Stack**: Python 3.13, Aiogram 3.24, SQLAlchemy (Async), PostgreSQL, Redis, Docker.

---

### 📂 Project Structure

```text
.
├── app/
│   ├── bot/                # Telegram layer (Handlers, Middlewares)
│   ├── services/           # Business logic (SubscriptionService)
│   ├── storage/            # Data layer (Repositories, Engine)
│   ├── models/             # SQLAlchemy models
│   ├── config.py           # Configuration (Pydantic)
│   ├── container.py        # DI Container
│   └── main.py             # Entry point
├── alembic/                # DB Migrations
├── entrypoint.sh           # Startup script
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Orchestration
└── pyproject.toml          # Dependencies (uv)
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
