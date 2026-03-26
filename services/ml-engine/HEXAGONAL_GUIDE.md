# Hexagonal cheat sheet

## Life of a request

```
            OUTSIDE THE HEXAGON                    INSIDE THE HEXAGON
        ┌───────────────────────┐     ┌──────────────────────────────────────┐
        │                       │     │                                      │
        │  main.py              │     │         ┌──────────────┐             │
        │  Starts the app,      │     │         │    DOMAIN    │             │
        │  calls bootstrap,     │     │         │              │             │
        │  registers routers    │     │         │  - Ports     │             │
        │                       │     │         │  - Exceptions│             │
        │  bootstrap.py         │     │         └──────┬───────┘             │
        │  Creates the adapter, │     │                │                     │
        │  stores in app.state  │     │         ┌──────┴───────┐             │
        │                       │     │         │ APPLICATION  │             │
        │  dependencies.py      │     │         │              │             │
        │  Wires adapter into   │     │         │  - Use cases │             │
        │  use case via Depends │     │         └──────┬───────┘             │
        │                       │     │                │                     │
        └───────────────────────┘     │  ┌─────────────┴──────────────┐      │
                                      │  │                            │      │
                                      │  │  ENTRYPOINTS    ADAPTERS   │      │
                                      │  │  (IN)           (OUT)      │      │
                                      │  │  Router         RteClient  │      │
                                      │  │                            │      │
                                      │  └────────────────────────────┘      │
                                      └──────────────────────────────────────┘
```

### Step-by-step: what happens when `POST /api/v1/energy/provider/token` is called

```
1. HTTP REQUEST arrives
   │
   ▼
2. ROUTER (entrypoints/http/router.py)
   FastAPI sees Depends(get_fetch_provider_token) and calls it.
   │
   ▼
3. DEPENDENCIES (dependencies.py) — outside the hexagon
   get_fetch_provider_token() is called:
     a. Retrieves RteApiClient from app.state (created during bootstrap)
     b. Creates FetchProviderToken(gateway=client)
     c. Returns the use case, ready to execute
   │
   ▼
4. ROUTER again
   Receives the use case, calls use_case.execute()
   │
   ▼
5. USE CASE (application/use_cases/fetch_provider_token.py)
   Calls self._gateway.get_token()
   Doesn't know it's talking to RTE — only knows the port contract.
   │
   ▼
6. PORT (domain/ports/energy_data_gateway.py)
   Just a contract: "any class with async get_token() -> str".
   Python resolves this to the concrete adapter via duck typing.
   │
   ▼
7. ADAPTER (infrastructure/rte/adapter.py)
   The real HTTP call: OAuth2 POST to RTE API.
   Returns the token, or raises EnergyProviderError.
   │
   ▼
8. BACK UP THE CHAIN
   Token bubbles back: adapter → use case → router → HTTP response.
   If error: EnergyProviderError is caught by the router → HTTP 502.
```

---

## File roles at a glance

### Inside the hexagon (dependencies point inward → domain)

| File | Role | Depends on |
|------|------|-----------|
| `domain/exceptions.py` | Business errors | nothing |
| `domain/ports/*.py` | Contracts (Protocol) | nothing |
| `application/use_cases/*.py` | Use cases | domain only |
| `infrastructure/<name>/adapter.py` | External API calls | domain only |
| `entrypoints/http/router.py` | HTTP endpoints + error handling | application + domain |

### Outside the hexagon (composition root — allowed to know everything)

| File | Role | Depends on |
|------|------|-----------|
| `<module>/bootstrap.py` | Creates adapters during app startup/shutdown | infrastructure |
| `<module>/dependencies.py` | Wires adapters into use cases via Depends() | application + infrastructure |
| `main.py` | App startup, calls bootstrap, registers routers | bootstrap + entrypoints |

> `bootstrap.py` and `dependencies.py` live at the **module root** (e.g. `energy/`),
> not inside any hexagonal layer.
> `main.py` is the global composition root — it should not know adapter or domain details.

## Naming rules

- **Generic names** (provider, gateway, forecast) → domain, application, entrypoints
- **Specific names** (rte, openweather, chronos) → only inside `infrastructure/<name>/`

---

## Step-by-step: creating a new `weather/` module from scratch

Target structure:

```
src/
├── weather/
│   ├── bootstrap.py                   # init/shutdown (creates OpenWeatherClient)
│   ├── dependencies.py                # DI wiring (composition root, outside the hexagon)
│   ├── domain/
│   │   ├── exceptions.py              # WeatherProviderError
│   │   └── ports/
│   │       └── weather_gateway.py     # Protocol WeatherGateway
│   ├── application/
│   │   └── use_cases/
│   │       └── fetch_forecast.py      # Use case FetchForecast
│   ├── entrypoints/
│   │   └── http/
│   │       └── router.py             # GET /forecast (catches WeatherProviderError)
│   └── infrastructure/
│       └── openweather/
│           ├── adapter.py             # OpenWeatherClient
│           └── settings.py            # OpenWeatherSettings (colocated with adapter)
└── main.py                            # Register bootstrap + router (no domain knowledge)
```

---

### 1. Domain exception

> `weather/domain/exceptions.py`

Skip if an existing exception already covers your case.

```python
class WeatherProviderError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Weather provider error {status_code}: {detail}")
```

---

### 2. Port (contract)

> `weather/domain/ports/weather_gateway.py`

Generic name, no provider reference. Just the "what", never the "how".

```python
from typing import Protocol

class WeatherGateway(Protocol):
    async def get_forecast(self, city: str) -> dict[str, float]: ...
```

---

### 3. Adapter (concrete implementation)

> `weather/infrastructure/openweather/adapter.py`

The only place that knows about the real API. Implements the port via duck typing.

```python
class OpenWeatherClient:
    async def get_forecast(self, city: str) -> dict[str, float]:
        response = await self.http_client.get("/v1/forecast", params={"q": city})
        if response.status_code != 200:
            raise WeatherProviderError(response.status_code, response.text)
        return response.json()
```

Settings live next to the adapter: `weather/infrastructure/openweather/settings.py`.

---

### 4. Use case

> `weather/application/use_cases/fetch_forecast.py` (+ `__init__.py` in `use_cases/`)

One file per use case. Only depends on the port, never on the adapter.

```python
from src.weather.domain.ports.weather_gateway import WeatherGateway

class FetchForecast:
    def __init__(self, gateway: WeatherGateway) -> None:
        self._gateway = gateway

    async def execute(self, city: str) -> dict[str, float]:
        return await self._gateway.get_forecast(city)
```

---

### 5. Bootstrap

> `weather/bootstrap.py` (module root, outside hexagonal layers)

Creates and destroys the adapter. Called by `main.py` lifespan.

```python
async def init_weather(app: FastAPI) -> None:
    settings = OpenWeatherSettings()
    app.state.weather_client = OpenWeatherClient(api_key=settings.api_key)

async def shutdown_weather(app: FastAPI) -> None:
    await app.state.weather_client.close()
```

---

### 6. Dependency wiring

> `weather/dependencies.py` (module root, outside hexagonal layers)

Assembles the adapter into the use case. The only file that knows both sides.

```python
def get_weather_client(request: Request) -> OpenWeatherClient:
    return cast(OpenWeatherClient, request.app.state.weather_client)

def get_fetch_forecast(
    client: OpenWeatherClient = Depends(get_weather_client),
) -> FetchForecast:
    return FetchForecast(gateway=client)
```

---

### 7. Router endpoint

> `weather/entrypoints/http/router.py`

Receives the use case via `Depends`, calls `execute()`, catches domain errors.

```python
@router.get("/forecast")
async def forecast(
    city: str,
    use_case: FetchForecast = Depends(get_fetch_forecast),
) -> dict[str, float]:
    try:
        return await use_case.execute(city)
    except WeatherProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
```

---

### 8. main.py — register the module

Two additions: bootstrap hooks and router. No domain imports.

```python
from src.weather.bootstrap import init_weather, shutdown_weather
from src.weather.entrypoints.http.router import router as weather_router

# in lifespan:
await init_weather(app)
# in shutdown:
await shutdown_weather(app)

# after app creation:
app.include_router(weather_router, prefix="/api/v1/weather")
```

---

Each module (`energy/`, `weather/`, ...) is **self-contained** with its own hexagonal layers.
`main.py` only sees `bootstrap` + `router` — never adapters, settings, or domain exceptions.
