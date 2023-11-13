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

def get_frameNumberFromSecond30Fps(second):
    return round(second * 30)

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

def get_significant_change_times_from_audio(audio_file_path, rms_window_length=0.02, rms_hop_length=0.01, 
                  change_threshold_factor=2.5, cooldown_time=0.2, low_level_percentile=25):
    # Load the audio file
    y, sr = librosa.load(audio_file_path, sr=None)

    # Calculate the RMS energy for each frame
    frame_length = int(rms_window_length * sr)
    hop_length = int(rms_hop_length * sr)
    rms_energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

    # Smooth the RMS energy using a moving average
    smooth_rms_energy = np.convolve(rms_energy, np.ones(3)/3, mode='valid')

    # Calculate the change in RMS energy between consecutive frames
    rms_change = np.diff(smooth_rms_energy)

    # Define 'low' RMS energy level as a percentile of the RMS energy
    low_rms_level = np.percentile(smooth_rms_energy, low_level_percentile)

    # Define a threshold for significant RMS change
    rms_change_threshold = np.median(np.abs(rms_change)) * change_threshold_factor

    # Find points where RMS change is above the threshold and the previous RMS value is below the 'low' level
    significant_changes = np.where((rms_change > rms_change_threshold) & 
                                   (smooth_rms_energy[:-1] < low_rms_level))[0]

    # Convert frame numbers to time and apply cooldown (debouncing)
    significant_change_times = []
    last_time = 0
    for frame in significant_changes:
        time = librosa.frames_to_time(frame + 1, sr=sr, hop_length=hop_length)
        if time - last_time > cooldown_time:  # Apply cooldown period
            significant_change_times.append(time)
            last_time = time

    return significant_change_times

def generate_beep(duration=0.1, frequency=1000.0, sample_rate=22050):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    beep = np.sin(2 * np.pi * frequency * t) * 0.5
    return beep

def create_beep_audio(onset_times, sample_rate=22050, output_file_path='beep_audio.wav'):
    if not onset_times:
        raise ValueError("Onset times array is empty")

    # Generate a beep sound
    beep_duration = 0.1  # duration of the beep in seconds
    beep = generate_beep(duration=beep_duration, frequency=1000.0, sample_rate=sample_rate)

    # Calculate the duration of the audio based on the last onset time
    max_onset_time = max(onset_times)
    audio_duration = max_onset_time + beep_duration

    # Create a silent audio signal of the required length
    silent_audio = np.zeros(int(audio_duration * sample_rate))

    # Insert the beep at each onset time
    for onset_time in onset_times:
        start_sample = int(onset_time * sample_rate)
        end_sample = start_sample + len(beep)
        
        # Ensure the beep doesn't go past the end of the audio
        if end_sample <= len(silent_audio):
            silent_audio[start_sample:end_sample] += beep
        else:
            # If the beep would go past the end, just add what can fit
            silent_audio[start_sample:] += beep[:len(silent_audio) - start_sample]
            
    # Write the beep audio signal to the output file
    sf.write(output_file_path, silent_audio, sample_rate)

def get_beeptrack_from_filepath(inputFilePath, outputFilePath):
    onset_times = get_significant_change_times_from_audio(inputFilePath)
    create_beep_audio(onset_times, output_file_path=outputFilePath)

def get_beeptrack_from_movesArray(movesArray, outputFilePath):
    create_beep_audio(movesArray, output_file_path=outputFilePath)

def get_framesArray_from_movesArray(movesArray):
    return [get_frameNumberFromSecond30Fps(x) for x in movesArray]