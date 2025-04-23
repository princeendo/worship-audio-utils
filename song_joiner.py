import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import audio_processing_helpers as aph

pattern = (
    r"^(?!\.)(?P<title>.+?)(?:-(?P<chord>[A-G](?:b|#)?)"
    r"(?:-with Background Vocals)?)"
    r"?-Trimmed_(?P<trim_length>\d+(?:\.\d+)?)s\.m4a$"
)


def has_bgv(filename: str) -> bool:
    return "with Background Vocals" in filename


@dataclass
class TrimmedMusicFile:
    path: str
    title: str = field(init=False)
    chord: str = field(init=False)
    trim_length: float = field(init=False)
    has_bgv: bool = field(init=False)

    def __post_init__(self):
        file = os.path.basename(self.path)
        dict_ = re.match(pattern, file).groupdict()
        self.title = dict_["title"]
        self.chord = dict_["chord"]
        self.trim_length = float(dict_["trim_length"])
        self.has_bgv = has_bgv(self.path)

    @property
    def directory(self):
        return os.path.dirname(self.path)


@dataclass
class SongData:
    bare: TrimmedMusicFile
    bgv: TrimmedMusicFile

    def __post_init__(self):
        assert not self.bare.has_bgv
        assert self.bgv.has_bgv
        for field_ in ["title", "chord", "trim_length"]:
            assert getattr(self.bare, field_) == getattr(self.bgv, field_)

    @property
    def wav_path(self):
        file = (
            f"{self.bare.title}-{self.bare.chord}"
            f"-Trimmed_{self.bare.trim_length}s-Split.wav"
        )
        return os.path.join(os.path.dirname(self.bare.path), file)

    def make_split_wav(self) -> None:
        return aph.create_split_track_file(
            self.bare.path,
            self.bgv.path,
            self.wav_path,
        )


def find_pairs(path: str) -> List[SongData]:
    tracker: Dict[Tuple[str, str, float], List[TrimmedMusicFile]] = {}
    for item in os.listdir(path):
        mo = re.match(pattern, item)
        if mo:
            try:
                music_file = TrimmedMusicFile(os.path.join(path, item))
                key = (
                    music_file.title,
                    music_file.chord,
                    music_file.trim_length,
                )
                if key not in tracker:
                    tracker[key] = [music_file]
                else:
                    tracker[key].append(music_file)
            except Exception as e:
                print(f"Error processing file {item}: {e}")
    song_data: List[SongData] = []
    for list_ in tracker.values():
        if len(list_) == 2:
            bare, bgv = sorted(list_, key=lambda x: x.has_bgv)
            song_data.append(SongData(bare=bare, bgv=bgv))
    return song_data
