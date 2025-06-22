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


def detect_nonsilent_ranges(
    audio: AudioSegment,
    min_silence_len: int = 500,
    silence_thresh: int = -40,
    seek_step: int = 1,
) -> list[tuple[float, float]]:
    """
    非無音区間を検出
    """
    ranges = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        seek_step=seek_step,
    )
    # 結果は [ [開始ms, 終了ms], … ] なので秒単位へ整形
    return [(start/1000, end/1000) for start, end in ranges]
