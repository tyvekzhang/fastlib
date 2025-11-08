# Fastlib
High performance, easy to use, fast to code, ready for production

## Quick Start
1. Download dependencies with [uv](https://docs.astral.sh/uv)
```shell
# Default
uv add fastlib

# MySQL
uv add fastlib[mysql]

# PgSQL
uv add fastlib[pgsql]
```

2. Setup [alembic](https://github.com/sqlalchemy/alembic)

3. Paste files to your project
[main.py](https://github.com/tyvekzhang/biohunter/blob/main/main.py)
[server.py](https://github.com/tyvekzhang/biohunter/blob/main/src/main/app/server.py)
[config.yml](https://github.com/tyvekzhang/biohunter/blob/main/src/main/resource/config.yml)

4. Run the server

```shell
uv run main.py
```

## License

[MIT](https://opensource.org/licenses/MIT)
