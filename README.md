# Aplikacja do Zarządzania Notatkami - Microservices Architecture

Pełna aplikacja typu full-stack wykorzystująca architekturę mikroserwisów:
- **Frontend**: Aplikacja SPA w React z TypeScript
- **3 Microservices**: Users, Notes, Analytics (FastAPI)
- **3 Databases**: PostgreSQL per service (Database per Service pattern)
- **Message Broker**: RabbitMQ dla komunikacji asynchronicznej

## Architektura Mikroserwisów

```
                                 ┌─────────────────┐
                                 │   Frontend      │
                                 │   (React)       │
                                 │   Port 3000     │
                                 └────────┬────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
                    ▼                     ▼                     ▼
         ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
         │  Users Service   │  │  Notes Service   │  │Analytics Service │
         │   (FastAPI)      │  │   (FastAPI)      │  │   (FastAPI)      │
         │   Port 8002      │  │   Port 8001      │  │   Port 8003      │
         └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
                  │                     │                     │
                  │                     │                     │
                  ▼                     ▼                     ▼
         ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
         │   users_db       │  │   notes_db       │  │  analytics_db    │
         │  PostgreSQL      │  │  PostgreSQL      │  │  PostgreSQL      │
         │   Port 5433      │  │   Port 5432      │  │   Port 5434      │
         └──────────────────┘  └──────────────────┘  └──────────────────┘
                  │                     │                     │
                  └─────────────────────┼─────────────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │    RabbitMQ      │
                              │  Message Broker  │
                              │  Ports 5672,     │
                              │        15672     │
                              └──────────────────┘
```

## Struktura Projektu

```
.
├── backend/
│   ├── shared/                      # Współdzielone narzędzia
│   │   ├── config.py               # Konfiguracja wspólna
│   │   ├── jwt_utils.py            # Uwierzytelnianie JWT
│   │   ├── rabbitmq_client.py      # Klient RabbitMQ
│   │   └── event_schemas.py        # Schematy zdarzeń
│   │
│   ├── users_service/              # Mikroserwis Users
│   │   ├── app/
│   │   │   ├── main.py            # Główny plik aplikacji
│   │   │   ├── database.py        # Konfiguracja bazy danych
│   │   │   ├── models.py          # Modele użytkowników
│   │   │   ├── schemas.py         # Schematy Pydantic
│   │   │   ├── auth.py            # Logika uwierzytelniania
│   │   │   └── routers/
│   │   │       └── users.py       # Endpointy API
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── notes_service/              # Mikroserwis Notes
│   │   ├── app/
│   │   │   ├── main.py            # Główny plik aplikacji
│   │   │   ├── database.py        # Konfiguracja bazy danych
│   │   │   ├── models.py          # Modele notatek
│   │   │   ├── schemas.py         # Schematy Pydantic
│   │   │   └── routers/
│   │   │       └── notes.py       # Endpointy API
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── analytics_service/          # Mikroserwis Analytics
│       ├── app/
│       │   ├── main.py            # Główny plik aplikacji
│       │   ├── database.py        # Konfiguracja bazy danych
│       │   ├── models.py          # Modele analityczne
│       │   ├── schemas.py         # Schematy Pydantic
│       │   ├── event_processor.py # Konsumenty zdarzeń
│       │   └── routers/
│       │       └── analytics.py   # Endpointy API
│       ├── Dockerfile
│       └── requirements.txt
│
├── frontend/                        # Frontend React
│   ├── src/
│   │   ├── components/
│   │   │   ├── NoteForm.tsx
│   │   │   └── NotesList.tsx
│   │   ├── App.tsx
│   │   └── ...
│   ├── Dockerfile
│   └── package.json
│
└── docker-compose.yml              # Orkiestracja mikroserwisów

## Wymagania

- Docker (wersja 20.x lub nowsza)
- Docker Compose (wersja 2.x lub nowsza)

## Uruchomienie

### Uruchomienie wszystkich serwisów

```bash
docker-compose up --build
```

Aplikacja będzie dostępna pod adresami:
- **Frontend**: http://localhost:3000
- **Users Service API**: http://localhost:8002
- **Notes Service API**: http://localhost:8001
- **Analytics Service API**: http://localhost:8003
- **RabbitMQ Management UI**: http://localhost:15672 (login: rabbitmq / rabbitmq)

**Dokumentacja API (Swagger)**:
- Users: http://localhost:8002/docs
- Notes: http://localhost:8001/docs
- Analytics: http://localhost:8003/docs

**Bazy danych**:
- notes_db: localhost:5432
- users_db: localhost:5433
- analytics_db: localhost:5434

### Uruchomienie w tle

```bash
docker-compose up -d --build
```

### Zatrzymanie aplikacji

```bash
docker-compose down
```

### Zatrzymanie z usunięciem wolumenów (baza danych)

```bash
docker-compose down -v
```

## Funkcjonalności

### 1. Users Service (Port 8002)
**Odpowiedzialność**: Zarządzanie użytkownikami i uwierzytelnianie
- Rejestracja nowych użytkowników
- Logowanie i generowanie tokenów JWT
- Zarządzanie profilami użytkowników
- Publikowanie zdarzeń użytkownika do RabbitMQ
- **Baza danych**: users_db (PostgreSQL)

**Endpointy**:
- `POST /users/register` - Rejestracja użytkownika
- `POST /users/login` - Logowanie (zwraca JWT token)
- `GET /users/me` - Pobierz dane zalogowanego użytkownika
- `PUT /users/me` - Aktualizuj profil użytkownika
- `DELETE /users/me` - Usuń konto użytkownika
- `GET /users/{user_id}` - Pobierz dane użytkownika (publiczny)

### 2. Notes Service (Port 8001)
**Odpowiedzialność**: Zarządzanie notatkami
- CRUD operations dla notatek (wymagane JWT)
- Notatki są przypisane do użytkowników (user_id)
- Publikowanie zdarzeń notatek do RabbitMQ
- **Baza danych**: notes_db (PostgreSQL)

**Endpointy** (wszystkie wymagają JWT):
- `POST /notes/` - Utwórz notatkę
- `GET /notes/` - Pobierz wszystkie notatki użytkownika
- `GET /notes/{note_id}` - Pobierz konkretną notatkę
- `PUT /notes/{note_id}` - Zaktualizuj notatkę
- `DELETE /notes/{note_id}` - Usuń notatkę

### 3. Analytics Service (Port 8003)
**Odpowiedzialność**: Analityka i statystyki
- Konsumuje zdarzenia z RabbitMQ
- Gromadzi statystyki użytkowników
- Śledzi zdarzenia notatek
- **Baza danych**: analytics_db (PostgreSQL)

**Endpointy**:
- `GET /analytics/users/me/statistics` - Statystyki zalogowanego użytkownika
- `GET /analytics/users/{user_id}/events/notes` - Historia zdarzeń notatek
- `GET /analytics/users/{user_id}/events/activity` - Historia aktywności użytkownika
- `GET /analytics/system/statistics` - Statystyki całego systemu (publiczny)

### 4. Message Broker (RabbitMQ)
**Odpowiedzialność**: Komunikacja asynchroniczna między serwisami
- **Exchanges**:
  - `users.events` - Zdarzenia użytkowników
  - `notes.events` - Zdarzenia notatek
- **Queues**:
  - `analytics.users.queue` - Zdarzenia użytkowników dla Analytics
  - `analytics.notes.queue` - Zdarzenia notatek dla Analytics

**Typy zdarzeń**:
- `user.registered` - Nowy użytkownik zarejestrowany
- `user.logged_in` - Użytkownik zalogowany
- `note.created` - Notatka utworzona
- `note.updated` - Notatka zaktualizowana
- `note.deleted` - Notatka usunięta

### 5. Frontend (React + TypeScript)
- Responsywny interfejs użytkownika
- Rejestracja i logowanie użytkowników
- Zarządzanie notatkami (CRUD)
- Wyświetlanie statystyk użytkownika
- Komunikacja z wieloma mikroserwisami

## Testowanie Mikroserwisów

### 1. Testowanie przez Swagger UI

Każdy mikroserwis ma własną dokumentację Swagger:
- Users: http://localhost:8002/docs
- Notes: http://localhost:8001/docs
- Analytics: http://localhost:8003/docs

### 2. Przykładowy przepływ testowy

#### Krok 1: Rejestracja użytkownika
```bash
curl -X POST http://localhost:8002/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

#### Krok 2: Logowanie
```bash
curl -X POST http://localhost:8002/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

Odpowiedź zwraca token JWT:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Krok 3: Utworzenie notatki (z tokenem JWT)
```bash
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8001/notes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Moja pierwsza notatka",
    "content": "To jest treść mojej notatki"
  }'
```

#### Krok 4: Pobierz swoje notatki
```bash
curl -X GET http://localhost:8001/notes/ \
  -H "Authorization: Bearer $TOKEN"
```

#### Krok 5: Sprawdź statystyki
```bash
curl -X GET http://localhost:8003/analytics/users/me/statistics \
  -H "Authorization: Bearer $TOKEN"
```

#### Krok 6: Sprawdź statystyki systemowe (publiczny endpoint)
```bash
curl -X GET http://localhost:8003/analytics/system/statistics
```

### 3. Testowanie RabbitMQ

Otwórz RabbitMQ Management UI: http://localhost:15672
- Login: `rabbitmq`
- Password: `rabbitmq`

W UI możesz:
- Zobaczyć exchanges: `users.events`, `notes.events`
- Zobaczyć queues: `analytics.users.queue`, `analytics.notes.queue`
- Monitorować przepływ wiadomości
- Sprawdzać statystyki konsumentów

## Konfiguracja

### Zmienne środowiskowe

#### Backend
- `DATABASE_URL` - URL połączenia z bazą danych (domyślnie: `postgresql://user:password@db:5432/dbname`)

#### Frontend
- `REACT_APP_API_URL` - URL backendu API (domyślnie: `http://localhost:8000`)

### Modyfikacja portów

Możesz zmienić porty w pliku `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "3000:80"  # zmień 3000 na inny port

  backend:
    ports:
      - "8000:8000"  # zmień 8000 na inny port

  db:
    ports:
      - "5432:5432"  # zmień 5432 na inny port
```

## Rozwój lokalny

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Testowanie

### Testowanie API

Otwórz przeglądarkę i przejdź do:
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/redoc - ReDoc

### Testowanie frontendu

Otwórz przeglądarkę i przejdź do:
- http://localhost:3000

## Monitoring

### Sprawdzanie logów

```bash
# Wszystkie serwisy
docker-compose logs -f

# Konkretny serwis
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Sprawdzanie statusu kontenerów

```bash
docker-compose ps
```

## Troubleshooting

### Problem z połączeniem do bazy danych

Upewnij się, że kontener bazy danych jest w pełni uruchomiony:

```bash
docker-compose logs db
```

### Frontend nie może połączyć się z backendem

1. Sprawdź, czy backend działa: `curl http://localhost:8000`
2. Sprawdź konfigurację CORS w `backend/app/main.py`
3. Sprawdź zmienną `REACT_APP_API_URL` w konfiguracji frontendu

### Rebuild kontenerów

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## Technologie

### Microservices Stack
- **Backend Framework**: FastAPI
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Message Broker**: RabbitMQ 3.12
- **Message Client**: pika
- **Databases**: PostgreSQL 15 (3 instances)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Styling**: CSS3
- **HTTP Client**: fetch API

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Nginx (frontend)

## Wzorce Architektoniczne

### 1. Database per Service
Każdy mikroserwis ma własną bazę danych:
- **Zalety**: Izolacja danych, niezależne skalowanie, swoboda wyboru technologii
- **Implementacja**: 3 osobne instancje PostgreSQL

### 2. Event-Driven Architecture
Komunikacja asynchroniczna przez RabbitMQ:
- **Zalety**: Luźne powiązanie, odporność na błędy, skalowalność
- **Implementacja**: Fanout exchanges, durable queues

### 3. API Gateway Pattern (opcjonalny)
Frontend komunikuje się bezpośrednio z serwisami:
- **Obecna implementacja**: Direct service calls
- **Przyszłość**: Możliwość dodania API Gateway (Nginx, Kong)

### 4. JWT Authentication
Bezstanowe uwierzytelnianie między serwisami:
- **Zalety**: Brak potrzeby współdzielenia sesji, skalowalność
- **Implementacja**: Shared JWT secret, token validation w każdym serwisie

## Zalety Architektury Mikroserwisów

1. **Skalowalność**: Każdy serwis można skalować niezależnie
2. **Odporność**: Awaria jednego serwisu nie zatrzymuje całego systemu
3. **Niezależne deployments**: Możliwość niezależnego wdrażania serwisów
4. **Elastyczność technologiczna**: Możliwość użycia różnych technologii
5. **Autonomia zespołów**: Różne zespoły mogą pracować nad różnymi serwisami
6. **Łatwiejsze utrzymanie**: Mniejsze, bardziej zrozumiałe bazy kodu

## Licencja

Ten projekt jest przykładową aplikacją edukacyjną.
