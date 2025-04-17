import os
from pydub import AudioSegment


def mix_down_to_one_channel(filename: str) -> AudioSegment:
    audio = AudioSegment.from_file(filename)
    return audio.set_channels(1)


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
