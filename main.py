import os
from highrise import BaseBot, User, Position
from highrise.__main__ import main as highrise_main
from radio import Radio
from config import OWNER_IDS, PREFIX

radio = Radio()

class MusicBot(BaseBot):
    async def on_start(self, session_metadata):
        print("Highrise Music Bot connected")

    async def on_chat(self, user: User, message: str):
        msg = message.strip()
        if not msg.startswith(PREFIX):
            return
        parts = msg[len(PREFIX):].strip().split(maxsplit=1)
        if not parts:
            return
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""
        uid = str(user.id)
        is_admin = uid in OWNER_IDS

        if command == "help":
            await self.highrise.chat(
                "!play <direct-audio-url> | !queue | !now | !skip (admin) | "
                "!pause (admin) | !resume (admin) | !clear (admin) | !radio"
            )
        elif command == "play":
            if not arg:
                await self.highrise.chat("Usage: !play <direct audio URL>")
                return
            if not arg.startswith(("https://", "http://")):
                await self.highrise.chat("Please provide a direct audio URL. Search-by-name is not enabled in this safe starter.")
                return
            item = await radio.add(arg, user.username or str(user.id))
            await self.highrise.chat(f"Added to radio queue: {item['title']}")
        elif command == "queue":
            items = await radio.queue_snapshot()
            if not items:
                await self.highrise.chat("The radio queue is empty.")
            else:
                lines = [f"{i+1}. {x['title']}" for i, x in enumerate(items[:8])]
                await self.highrise.chat("Radio queue:\\n" + "\\n".join(lines))
        elif command == "now":
            item = await radio.current()
            await self.highrise.chat("Now playing: " + (item["title"] if item else "Nothing"))
        elif command in ("skip", "pause", "resume", "clear"):
            if not is_admin:
                await self.highrise.chat("This command is for the radio admin.")
                return
            if command == "skip":
                await radio.skip()
                await self.highrise.chat("Skipped.")
            elif command == "pause":
                await radio.set_paused(True)
                await self.highrise.chat("Radio paused.")
            elif command == "resume":
                await radio.set_paused(False)
                await self.highrise.chat("Radio resumed.")
            else:
                await radio.clear()
                await self.highrise.chat("Queue cleared.")
        elif command == "radio":
            await self.highrise.chat("Listen to the radio: " + os.getenv("PUBLIC_BASE_URL", "").rstrip("/") + "/radio")

if __name__ == "__main__":
    # Configure HIGHRISE_ROOM_ID and HIGHRISE_API_TOKEN in Railway variables.
    highrise_main(MusicBot(), os.environ["HIGHRISE_ROOM_ID"], os.environ["HIGHRISE_API_TOKEN"])
