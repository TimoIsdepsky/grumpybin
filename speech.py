import asyncio
import edge_tts
import io
import sounddevice as sd
import soundfile as sf
from storage import FileStorageBackend
import random
import logging

logger = logging.getLogger(__name__)

def play_edge_tts():
    #voice="de-DE-KatjaNeural"
    voice="de-DE-SeraphinaMultilingualNeural"
    #voice="de-AT-IngridNeural"

    storage_backend = FileStorageBackend("lines")

    lines: list[str] = storage_backend.get_lines()

    rng = random.randint(0, lines.__len__() - 1)

    text = lines[rng].split(":")[1].strip()

    logger.debug(text)

    async def _speak():
        communicate = edge_tts.Communicate(text, voice)
        stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                stream.write(chunk["data"])
        stream.seek(0)
        data, samplerate = sf.read(stream)
        sd.play(data, samplerate=samplerate)
        sd.wait()

    asyncio.run(_speak())