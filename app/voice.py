import io
from pydub import AudioSegment


def convert_audio(content):
    s = io.BytesIO(content)
    audio=AudioSegment.from_file(s)
    audio = audio.set_frame_rate(16000)
    buf = io.BytesIO()
    audio.export(buf, format="wav")
    return buf.getvalue()
