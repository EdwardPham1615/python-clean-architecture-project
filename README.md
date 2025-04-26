# 🚀 Python Clean Architecture Project

## 📌 Overview

This repository demonstrates a **scalable and maintainable Python backend** following the **Clean Architecture** principles. It is designed to be adaptable across multiple infrastructures, including **SQL, NoSQL, message queues, and caches**. The project emphasizes:

- **Separation of concerns** to keep business logic independent of frameworks and databases.
- **Dependency Injection** to manage dependencies efficiently.
- **Unit of Work Pattern** to handle transactional consistency.
- **Modular design** to support extensibility and testability.

By following Clean Architecture, this project ensures that the core business logic remains **decoupled from external dependencies**, making it easier to scale, modify, and test.

---

## 📚 Understanding Clean Architecture

### 🏡 What is Clean Architecture?

**Clean Architecture**, proposed by Robert C. Martin (**Uncle Bob**), is a software design philosophy that ensures:

- **Independence from frameworks** – The business logic does not depend on external libraries.
- **Testability** – Core logic can be tested without external dependencies.
- **Separation of concerns** – Divides the system into layers with clear responsibilities.
- **Scalability & Maintainability** – Easy to extend and modify without breaking existing features.

### 🔄 Layered Structure of Clean Architecture

```
┌──────────────────────────────┐
│        Controllers          │  → Handles requests & responses (HTTP, gRPC, etc.)
├──────────────────────────────┤
│          Services           │  → Coordinates business logic & interacts with use cases
├──────────────────────────────┤
│          Use Cases          │  → Encapsulates core business logic
├──────────────────────────────┤
│ Infrastructures (DB, Cache) │  → Handles external dependencies like databases & queues
└──────────────────────────────┘
```

Each layer interacts **only with the layer directly below it**, ensuring minimal coupling.

---

## 🏰️ Key Design Patterns

### 🛠️ Dependency Injection (DI)

Dependency Injection is used to **decouple components** by injecting dependencies instead of creating them inside a class. It enables:

- **Easier testing** (mocking dependencies)
- **Improved modularity**
- **Greater flexibility**

🔹 Refer to the [dependency-injector](https://github.com/ets-labs/python-dependency-injector) library for implementation details.

### 🔄 Unit of Work (UoW)

The **Unit of Work pattern** ensures that multiple repository operations are **executed as a single transaction**.

- **Prevents partial updates** in case of failure.
- **Ensures database consistency**.

---

## 🏡 Project Structure

```
internal/
│── controllers/      # Handles requests and responses (endpoints)
│── domains/          # Core business logic (services, use cases, entities)
│── infrastructures/  # External dependencies (databases, caches, queues)
│── patterns/         # Dependency injection
└── main.py           # Application entry point
```

- **Controllers**: Define the API endpoints and route requests to services.
- **Domains**: Contains core business logic, including services and use cases.
- **Infrastructures**: Houses repositories and database interactions.
- **Patterns**: Implements design patterns like Dependency Injection and Unit of Work.
- **Main.py**: Initializes the application, including dependency injection and routing setup.

This modular structure ensures **scalability**, **testability**, and **maintainability**.

---

## ▶️ Running the Project

### Prerequisites

Ensure you have the following installed:

- Python 3.13+

- UV ([https://docs.astral.sh/uv/](https://docs.astral.sh/uv/))

- PostgreSQL 15+ (Use your own local PostgreSQL or you can use my docker-compose.dev.yaml)

- Keycloak 26.x (Optional) (Use your own local Keycloak with webhook extension [https://github.com/p2-inc/keycloak-events](...) or you can use my docker-compose.dev.yaml)

- OpenFGA 1.8.9 (Optional) (Use your own local OpenFGA or you can use my docker-compose.dev.yaml)

- Docker & Docker Compose (Optional)

- make (Optional)

### Installation & Setup

1. **Clone the Repository**

   ```sh
   git clone https://github.com/EdwardPham1615/python-clean-architecture-project.git
   cd python-clean-architecture-project
   ```

2. **Set Up a UV Virtual Environment**

   ```sh
   uv lock && uv sync
   ```

3. **Manage Relational Database Migrations**

   ```sh
   # using Alembic (https://alembic.sqlalchemy.org/en/latest/)

   # For manually generate migration files base on your need
   alembic revision -m <name_version>

   # For auto generate migrations files base on your models
   alembic revision --autogenerate -m <name_version>
   ```

4. **Manage Keycloak and Webhook Config**

   ```sh
   This section is optional and our repo still working without Keycloak, but you need to implement another authentication service by yourself !!!
   
   In this repo, i use Phasetwo as an example of authentication service integration (https://phasetwo.io/docs/introduction/), is basically Keycloak with extensions.
   But you can just use an original Keycloak and then install webhook extension with it (optional).
   
   Step 1: Setup your Keycloak using the original documents 
   https://www.keycloak.org/documentation.
   
   Step 2: Setup webhooks (optional)
   Follow this document https://phasetwo.io/docs/audit-logs/webhooks/
   And checkout my folder "examples/external_authentication_service_webhook_crud".
   ```

5. **Setup OpenFGA**

   ```sh
   This section is optional and our repo still working without OpenFGA, but you need to implement another authorization service by yourself !!!
   
   In this repo, we need a token, a store_id and a authorization_model_id.
   Follow the official document of OpenFGA for details (https://openfga.dev/docs/getting-started/setup-openfga/overview).
   
   Step 1: Generate a new token for OpenFGA then config it for docker and also our app, we use a simple authen method (https://openfga.dev/docs/getting-started/setup-openfga/configure-openfga#pre-shared-key-authentication).
   Step 2: Create a new store, use playground to make it simple or you can follow this (https://openfga.dev/docs/getting-started/create-store).
   Step 3: Create a new authorization_model_id model, use playground to make it simple or you can follow this (https://openfga.dev/docs/getting-started/configure-model).
            I have already create a sample of authorization model here "internal/infrastructures/external_rebac_authorization_service/openfga_client/authorization_model_versions/00001_autho_model.dsl".
   Step 4: Config token, store_id and authorization_model_id to our app.
   ```

6. **Start the Application**

   ```sh
   python main.py
   ```

7. **Alternative run with docker**

   ```sh
   # if you do not want to start from scratch, just run with docker
   # using commands from Makefile
   
   # build an image
   make build
   
   # start
   make start
   
   # stop
   make stop
   
   # restart
   make restart

   ```
   
8. **Access the API**

   - Use `http://127.0.0.1:8082/docs` for Swagger UI.
   - Use `http://127.0.0.1:8082/redoc` for Redoc documentation.
   - Use `http://127.0.0.1:5000/healh-check` for health check port
