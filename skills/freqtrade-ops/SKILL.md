---
name: freqtrade-ops
description: Start/stop/restart the Freqtrade Docker setup, reload strategy/config changes, and verify the bot/UI is running correctly in /Users/scott/Desktop/trade/ft_userdata.
---

# Freqtrade Docker Ops (ft_userdata)

Use this skill when the user asks how to start/stop/restart the bot, reload config, change strategies, or verify the UI after changes.

## Assumptions

- Working directory is `/Users/scott/Desktop/trade/ft_userdata`.
- The bot is run via `docker compose` and the strategy lives in `user_data/strategies/`.

## Choose the correct action

1) **Only strategy file changed** (`user_data/strategies/*.py`)  
   - Restart container to load new code:
     ```bash
     docker compose restart freqtrade
     ```

2) **Config or env changed** (`user_data/config.json`, `.env.*`)  
   - Restart container:
     ```bash
     docker compose restart freqtrade
     ```

3) **docker-compose.yml changed** (strategy name, ports, env_file, volumes)  
   - Recreate container:
     ```bash
     docker compose up -d --force-recreate
     ```

4) **Stop/Start**  
   - Stop:
     ```bash
     docker compose stop freqtrade
     ```
   - Start:
     ```bash
     docker compose start freqtrade
     ```

## Verification (always do)

1) Container state:
```bash
docker compose ps
```

2) Strategy actually loaded:
```bash
docker compose logs --tail=80 | grep "Strategy:"
```

3) UI reachable:
- Open `http://127.0.0.1:8080/`

If logs are noisy, filter further:
```bash
docker compose logs --tail=80 | grep "Using resolved strategy"
```

## Notes

- If `rg` is unavailable, use `grep`.
- If the UI shows the old strategy, use `docker compose up -d --force-recreate`.
