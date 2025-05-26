import os
import random
import pygame

def play_random_music_wav(music_dir=None):
    if music_dir is None:
        music_dir = os.path.join('data', 'audio', 'music')
    wav_files = [f for f in os.listdir(music_dir) if f.lower().endswith('.wav')]
    if not wav_files:
        print("No .wav files found in", music_dir)
        return
    chosen = random.choice(wav_files)
    path = os.path.join(music_dir, chosen)
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        print(f"Playing: {chosen}")
    except Exception as e:
        print(f"Failed to play {chosen}: {e}")

def play_sound_effect(default_path, sound_path=None, label=None):
    path = sound_path or default_path
    try:
        sound = pygame.mixer.Sound(path)
        sound.play()
        if label:
            print(f"Played {label} sound: {os.path.basename(path)}")
    except Exception as e:
        print(f"Failed to play {label or 'sound'} {path}: {e}")

def play_build_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/build1.wav', sound_path, 'build')

def play_pipette_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/pipette1.wav', sound_path, 'pipette')

def play_breaker_break_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/breaker-break1.wav', sound_path, 'breaker break')

def play_internet_outage_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/internet-outage1.wav', sound_path, 'internet outage')

def play_internet_reconnect_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/internet-reconnect1.wav', sound_path, 'internet reconnect')
