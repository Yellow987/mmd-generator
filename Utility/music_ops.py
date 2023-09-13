import librosa

def load_song_from_filepath(filepath):
    y, sr = librosa.load(filepath)
    return y, sr

def get_tempo(y, sr):
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    return tempo

def get_beatTimesInSeconds(y, sr):
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beatTimes = librosa.frames_to_time(beat_frames, sr=sr)
    return beatTimes

def get_songDurationInSeconds(y, sr):
    return librosa.get_duration(y=y, sr=sr)

def get_beatFrames30Fps_from_beatTimesInSeconds(beat_times):
    rounded_beat_times = [round(time * 30) for time in beat_times]
    return rounded_beat_times