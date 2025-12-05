# Python 3.x
import os
import time
import threading
import webbrowser
from dataclasses import dataclass
from pathlib import Path

import requests
from dotenv import load_dotenv

import logging
from logging.handlers import RotatingFileHandler

import pystray
from PIL import Image, ImageDraw

# ------------- CONFIG & ENV -------------

BASE_DIR = Path(__file__).resolve().parent

# Load .env file from the same folder
load_dotenv(BASE_DIR / ".env")


@dataclass
class Config:
    client_id: str
    client_secret: str
    streamer_login: str
    poll_interval_seconds: int = 180  # default: 3 minutes


TWITCH_OAUTH_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_STREAMS_URL = "https://api.twitch.tv/helix/streams"

# Global flag used to stop the main loop from the tray icon
running = True

# ------------- LOGGING SETUP -------------

LOG_FILE = BASE_DIR / "twitch_live_opener.log"


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("twitch_watcher")
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers if script is reloaded
    if not logger.handlers:
        handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=500_000,  # ~500 KB
            backupCount=3,
            encoding="utf-8",
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Optional: also log to console
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger


logger = setup_logger()


def get_config() -> Config:
    try:
        client_id = os.environ["TWITCH_CLIENT_ID"]
        client_secret = os.environ["TWITCH_CLIENT_SECRET"]
        streamer_login = os.environ["TWITCH_STREAMER_LOGIN"].lower()
    except KeyError as e:
        missing = e.args[0]
        msg = f"Missing environment variable {missing}. Did you set up your .env file?"
        logger.error(msg)
        raise SystemExit(msg) from e

    poll_interval = int(os.environ.get("POLL_INTERVAL", "180"))

    return Config(
        client_id=client_id,
        client_secret=client_secret,
        streamer_login=streamer_login,
        poll_interval_seconds=poll_interval,
    )


# ------------- TWITCH API FUNCTIONS -------------

def get_app_access_token(cfg: Config) -> str:
    """Get an app access token via client credentials."""
    logger.info("Requesting new Twitch API token...")
    resp = requests.post(
        TWITCH_OAUTH_URL,
        data={
            "client_id": cfg.client_id,
            "client_secret": cfg.client_secret,
            "grant_type": "client_credentials",
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    logger.info("Got Twitch API token.")
    return data["access_token"]


def is_streamer_live(cfg: Config, token: str) -> bool:
    """Return True if streamer is live, False otherwise."""
    headers = {
        "Client-Id": cfg.client_id,
        "Authorization": f"Bearer {token}",
    }
    params = {"user_login": cfg.streamer_login}

    resp = requests.get(TWITCH_STREAMS_URL, headers=headers, params=params, timeout=10)

    if resp.status_code == 401:
        # token expired or invalid
        raise PermissionError("Twitch token expired or invalid")

    resp.raise_for_status()
    data = resp.json()
    streams = data.get("data", [])
    return bool(streams)


# ------------- TRAY ICON -------------

def create_tray_image() -> Image.Image:
    """Create a simple tray icon image (purple dot in a circle)."""
    size = 64
    image = Image.new("RGB", (size, size), (40, 40, 40))
    draw = ImageDraw.Draw(image)
    # Outer circle
    draw.ellipse((8, 8, size - 8, size - 8), fill=(128, 0, 200))
    # Inner dot
    draw.ellipse((24, 24, size - 24, size - 24), fill=(255, 255, 255))
    return image


def on_quit(icon, item):
    """Menu item callback to quit the app."""
    global running
    logger.info("Quit requested from tray icon. Stopping watcher...")
    running = False
    icon.visible = False
    icon.stop()


def start_tray_icon():
    """Run the system tray icon event loop."""
    image = create_tray_image()
    menu = pystray.Menu(
        pystray.MenuItem("Quit", on_quit)
    )
    icon = pystray.Icon(
        "TwitchWatcher",
        image,
        f"Twitch Watcher - {os.environ.get('TWITCH_STREAMER_LOGIN', '')}",
        menu,
    )
    logger.info("Starting system tray icon.")
    icon.run()
    logger.info("Tray icon loop ended.")


# ------------- MAIN WATCH LOOP -------------

def watch_loop():
    cfg = get_config()
    logger.info(f"Monitoring Twitch channel: {cfg.streamer_login}")

    try:
        token = get_app_access_token(cfg)
    except Exception as e:
        logger.error(f"Failed to get Twitch token: {e}")
        return

    last_state_live = False

    global running
    while running:
        try:
            live_now = is_streamer_live(cfg, token)
        except PermissionError:
            logger.warning("Token expired. Refreshing...")
            try:
                token = get_app_access_token(cfg)
                live_now = is_streamer_live(cfg, token)
            except Exception as e:
                logger.error(f"Failed to refresh token: {e}")
                live_now = last_state_live
        except Exception as e:
            logger.error(f"Error checking stream status: {e}")
            live_now = last_state_live  # don't flip state on error

        if live_now and not last_state_live:
            url = f"https://www.twitch.tv/{cfg.streamer_login}"
            logger.info(f"{cfg.streamer_login} just went LIVE! Opening {url}")
            webbrowser.open(url)
        elif not live_now and last_state_live:
            logger.info(f"{cfg.streamer_login} appears to be offline now.")

        last_state_live = live_now

        time.sleep(cfg.poll_interval_seconds)

    logger.info("Watch loop has been stopped.")


def main():
    # Start tray icon in a separate thread so it doesn't block the watch loop
    tray_thread = threading.Thread(target=start_tray_icon, daemon=True)
    tray_thread.start()

    # Run the main watcher loop (blocks until running is set to False)
    watch_loop()

    # When watch_loop ends, script will exit (tray thread is daemon)


if __name__ == "__main__":
    main()

