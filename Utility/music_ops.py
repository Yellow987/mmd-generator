import librosa
import numpy as np
import soundfile as sf

def generate_beep_track(beatTimes, duration, sr, beep_duration=0.005, measure=4, meter=4):
    # Initialize an array to hold the audio data
    audio_data = np.zeros(int(sr * duration))
    
    # Generate a beep sound (this should be short)
    beep = np.sin(2 * np.pi * 440.0 * np.linspace(0, beep_duration, int(sr * beep_duration)))
    low_beep = np.sin(2 * np.pi * 220.0 * np.linspace(0, beep_duration, int(sr * beep_duration)))
    boom_beep = np.sin(2 * np.pi * 880.0 * np.linspace(0, beep_duration, int(sr * beep_duration)))

    # Insert the beep sound into audio_data at each beat time
    for i, beat_time in enumerate(beatTimes):
        if (i + 1) % (measure * meter) == 0:
            beep_to_use = boom_beep
        elif (i + 1) % measure == 0:
            beep_to_use = low_beep
        else:
            beep_to_use = beep
    
        start_sample = int(beat_time * sr)
        end_sample = start_sample + len(beep_to_use)
        
        if end_sample >= len(audio_data):
            end_sample = len(audio_data) - 1
            beep_to_use = beep_to_use[:end_sample - start_sample]
        
        audio_data[start_sample:end_sample] = beep_to_use[:end_sample - start_sample]
    
    # Normalize the audio data
    audio_data = 0.5 * audio_data / np.max(np.abs(audio_data))
    sf.write('beep_track3.wav', audio_data, sr)

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

def get_secondFromFrameNumber30Fps(frame_number):
    return frame_number / 30

def get_songDurationInSeconds(y, sr):
    return librosa.get_duration(y=y, sr=sr)

def get_beatFrames30Fps_from_beatTimesInSeconds(beat_times):
    rounded_beat_times = [round(time * 30) for time in beat_times]
    return rounded_beat_times

def get_beatFrames_from_filepath(filepath):
    y, sr = load_song_from_filepath(filepath)
    beat_times = get_beatTimesInSeconds(y, sr)
    beat_frames = get_beatFrames30Fps_from_beatTimesInSeconds(beat_times)
    return beat_frames