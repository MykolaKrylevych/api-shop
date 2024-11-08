# RESTFUL API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-d82c0f?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-008C54?style=for-the-badge&logo=stripe&logoColor=white)

**API Shop** is a FastAPI-powered RESTful API for managing a shop's inventory, orders, and customer information. The
project uses Docker for containerization and PostgreSQL as the primary database. Redis is utilized for caching to ensure
efficient data retrieval.

## Features

- **CRUD Operations** for products, cart, category and users.
- **User Authentication** with token-based authorization and Fastapi-Users Integration.
- **Order Management** for creating and monitoring orders.
- **Stripe Integration** for payment processing.
- **Redis Caching** for optimizing data retrieval.
- **Dockerized Setup** for seamless deployment.

## Requirements

- Python 3.9+
- Docker
- FastAPI
- PostgreSQL
- Redis
- Stripe API

## Installation

1. **Clone the repository**

```bash
   git clone https://github.com/MykolaKrylevych/api-shop.git
   cd api-shop
```

2. **Create a virtual environment (optional but recommended)**

```bash 
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required dependencies:

```bash
  pip install -r requirements.txt
```
4. Set up the environment variables:
```dotenv
POSTGRES_USER=POSTGRES_USER
POSTGRES_PASSWORD=POSTGRES_PASSWORD
POSTGRES_SERVER=POSTGRES_SERVER
POSTGRES_PORT=POSTGRES_PORT
POSTGRES_DB=POSTGRES_DB
USERMANAGER_SECRET=USERMANAGER_SECRET
REDIS_URL=REDIS_URL
STRIPE_SECRET_KEY=STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=STRIPE_PUBLISHABLE_KEY
WEBHOOK_SECRET=WEBHOOK_SECRET
```
5. Set up migrations (alembic)
```bash
alembic init alembic
alembic upgrade head
```
6. Start the FastAPI server, you can also use Docker-compose:
```bash
uvicorn app.main:app --reload
docker-compose up
```