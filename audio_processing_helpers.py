import os
from pydub import AudioSegment
import numpy as np
from scipy.signal import correlate
from numpy.typing import ArrayLike
from typing import Optional


def mix_down_to_one_channel(
    filename: str,
    sample_rate: Optional[int] = None,
) -> AudioSegment:
    audio = AudioSegment.from_file(filename)
    mono = audio.set_channels(1)
    if sample_rate is not None:
        mono = mono.set_frame_rate(sample_rate)
    return mono


def make_stereo_track(left: AudioSegment, right: AudioSegment) -> AudioSegment:
    return AudioSegment.from_mono_audiosegments(left, right)


def make_split_track(
    left_channel_file: str,
    right_channel_file: str,
) -> AudioSegment:
    left_mono = mix_down_to_one_channel(left_channel_file)
    right_mono = mix_down_to_one_channel(right_channel_file)
    return make_stereo_track(left_mono, right_mono)


def create_split_track_file(
    left_channel_file: str, right_channel_file: str, output_file: str
) -> None:
    stereo = make_split_track(left_channel_file, right_channel_file)
    stereo.export(output_file, format=os.path.splitext(output_file)[1][1:])


def load_audio_array(file: str, sample_rate: int = 16000) -> ArrayLike:
    audio = mix_down_to_one_channel(file, sample_rate=sample_rate)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples /= np.max(np.abs(samples))
    return samples


def audio_offset(
    reference_file: str, file_that_is_offset: str, sample_rate: int = 16000
) -> np.float64:
    dataA = load_audio_array(reference_file, sample_rate)
    dataB = load_audio_array(file_that_is_offset, sample_rate)

    correlation = correlate(dataB, dataA, mode="full")
    lag = correlation.argmax() - (len(dataA) - 1)
    return lag / sample_rate
