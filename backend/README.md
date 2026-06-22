# SeenIt na homelabie — step by step

Stack: PostgreSQL + FastAPI w Dockerze. Schemat i dane tworzy `db/init/init.sql`
(Postgres odpala go sam przy pierwszym starcie). Porty na hoście: **API 12500**,
**Postgres 12543**.

```
seenit-homelab/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── main.py
└── db/init/init.sql      <- schemat + dane (auto-run przez Postgres)
```

---



## Krok 1 — wgraj projekt na homelaba
```bash
git clone <twoje-repo> seenit && cd seenit
# albo z laptopa:  scp -r seenit-homelab user@homelab:~/seenit
```

## Krok 2 — konfiguracja
```bash
cp .env.example .env
```
W `.env` ustaw **mocne** `POSTGRES_PASSWORD` i `SECRET_KEY`
(`openssl rand -hex 32`). Pamiętaj zmienić hasło też w `DATABASE_URL`.

## Krok 3 — start
```bash
docker compose up -d --build
```
Co się dzieje: wstaje `db`, czeka na healthcheck, Postgres przy pierwszym
starcie wykonuje `db/init/init.sql` (tabele + dane demo), potem wstaje `api`.
Podgląd logów:
```bash
docker compose logs -f
```

## Krok 4 — sprawdź, że żyje
Z dowolnego komputera w sieci (zamień IP na adres homelaba):
```bash
curl http://192.168.x.x:12500/health        # {"status":"ok"}
```
Swagger: `http://192.168.x.x:12500/docs`

## Krok 5 — pgAdmin / psql
Połączenie do bazy z zewnątrz:
- host: **IP homelaba** (lub localhost, jeśli pgAdmin jest na homelabie)
- port: **12543**
- user / db: `seenit` / `seenit`, hasło: to z `.env`

Konta testowe (już w bazie):
`admin / admin123` · `kuba / kuba123` · `ola / ola123`

## Krok 6 — firewall
Otwórz porty na homelabie (przykład ufw):
```bash
sudo ufw allow 12500/tcp     # API
sudo ufw allow 12543/tcp     # Postgres (rozważ ograniczenie do swojej sieci)
```
Bezpieczeństwo: port bazy (12543) najlepiej wystawić tylko w LAN, nie na świat.

---

## Rzeczy, które MUSISZ wiedzieć (częste pułapki)

**init.sql odpala się tylko raz.** Działa wyłącznie, gdy wolumen danych jest
pusty. Zmieniłeś skrypt i chcesz, żeby wjechał od nowa? Skasuj dane:
```bash
docker compose down -v      # -v kasuje wolumen pgdata -> przy up init.sql leci znowu
docker compose up -d --build
```
Bez `-v` Twoje zmiany w `init.sql` zostaną zignorowane (baza już istnieje).

**Duże porty to TYLKO strona hosta.** W środku kontenerów nic się nie zmienia:
Postgres dalej słucha na 5432, API na 8000. Dlatego `DATABASE_URL` wskazuje
`db:5432`, a NIE `db:12543`. Mapowanie `12543:5432` dotyczy tylko dostępu z zewnątrz.

**restart: unless-stopped.** Gdy homelab się zrestartuje (prąd, aktualizacja),
kontenery wstaną same. Bez tego po reboocie projekt by nie wrócił.

**Dane przeżywają restart, ale nie `down -v`.** Wolumen `pgdata` trzyma bazę
między restartami. Tylko jawne `down -v` go kasuje.

---

## init.sql vs Alembic
Ta wersja używa `init.sql` jako JEDYNEGO właściciela schematu — najprościej na
homelab. Jeśli wolisz Alembic z wcześniejszego szkieletu, wybierz JEDNO:
albo `init.sql` tworzy tabele, albo Alembic — nie oba naraz (inaczej drugi
wywali się, bo tabele już istnieją).
