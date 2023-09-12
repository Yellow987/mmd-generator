import librosa

def get_tempo(filename):
    y, sr = librosa.load(filename)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    return tempo

def get_beatTimesInSeconds(audio_file_path):
    # Load the audio file; the default sample rate is 22,050 Hz
    audio_data, sample_rate = librosa.load(audio_file_path)
    
    # Perform beat tracking
    tempo, beat_frames = librosa.beat.beat_track(audio_data, sr=sample_rate)
    
    # Convert beat frames to time (in seconds)
    beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)
    
    return beat_times

def get_beatFrames30Fps_from_beatTimesInSeconds(beat_times):
    # Multiply each element in the array by 30 and round to the nearest integer
    rounded_beat_times = [round(time * 30) for time in beat_times]
    return rounded_beat_times