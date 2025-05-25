import os
import random
import pygame

def play_random_music_wav(music_dir=None):
    """
    Play a random .wav file from the given music_dir using pygame.mixer.music.
    If music_dir is None, defaults to 'data/audio/music'.
    """
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

def play_build_sound(sound_path=None):
    """
    Play a build sound effect from the given path using pygame.mixer.Sound.
    If sound_path is None, defaults to 'data/audio/sounds/build1.wav'.
    """
    if sound_path is None:
        sound_path = os.path.join('data', 'audio', 'sounds', 'build1.wav')
    try:
        sound = pygame.mixer.Sound(sound_path)
        sound.play()
        print(f"Played build sound: {os.path.basename(sound_path)}")
    except Exception as e:
        print(f"Failed to play build sound {sound_path}: {e}")

def play_pipette_sound(sound_path=None):
    """
    Play a pipette sound effect from the given path using pygame.mixer.Sound.
    If sound_path is None, defaults to 'data/audio/sounds/pipette1.wav'.
    """
    if sound_path is None:
        sound_path = os.path.join('data', 'audio', 'sounds', 'pipette1.wav')
    try:
        sound = pygame.mixer.Sound(sound_path)
        sound.play()
        print(f"Played pipette sound: {os.path.basename(sound_path)}")
    except Exception as e:
        print(f"Failed to play pipette sound {sound_path}: {e}")

def play_breaker_break_sound(sound_path=None):
    """
    Play a breaker break sound effect from the given path using pygame.mixer.Sound.
    If sound_path is None, defaults to 'data/audio/sounds/breaker-break1.wav'.
    """
    if sound_path is None:
        sound_path = os.path.join('data', 'audio', 'sounds', 'breaker-break1.wav')
    try:
        sound = pygame.mixer.Sound(sound_path)
        sound.play()
        print(f"Played breaker break sound: {os.path.basename(sound_path)}")
    except Exception as e:
        print(f"Failed to play breaker break sound {sound_path}: {e}")
