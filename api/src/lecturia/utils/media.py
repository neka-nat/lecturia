from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def remove_long_silence(
    audio: AudioSegment,
    silence_thresh: int = -40,
    min_silence_duration_ms: int = 4000,
) -> AudioSegment:
    nonsilent_ranges = detect_nonsilent(
        audio,
        min_silence_len=min_silence_duration_ms,
        silence_thresh=silence_thresh,
    )
    result_audio = AudioSegment.empty()
    for start, end in nonsilent_ranges:
        result_audio += audio[start:end]
        result_audio += AudioSegment.silent(duration=1000)

    return result_audio
