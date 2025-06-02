import os
import random
import pygame
import sys
from game_core.config import resource_path

def play_random_music_wav(music_dir=None):
    if music_dir is None:
        music_dir = resource_path(os.path.join('data', 'audio', 'music'))
    wav_files = [f for f in os.listdir(music_dir) if f.lower().endswith(('.wav', '.mp3'))]
    if not wav_files:
        print("No .wav or .mp3 files found in", music_dir)
        return
    chosen = random.choice(wav_files)
    path = os.path.join(music_dir, chosen)
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        print(f"Playing: {chosen}")
    except Exception as e:
        print(f"Failed to play {chosen}: {e}")

def play_sound_effect(default_path, sound_path=None):
    path = resource_path(sound_path or default_path)
    try:
        sound = pygame.mixer.Sound(path)
        sound.play()
    except Exception as e:
        print(f"Failed to play sound {path}: {e}")

def play_build_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/build1.wav', sound_path)

def play_pipette_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/pipette1.wav', sound_path)

def play_breaker_break_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/breaker-break1.wav', sound_path)

def play_system_out_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/system-out1.wav', sound_path)

def play_system_back_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/system-back1.wav', sound_path)

def play_power_outage_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/power-outage1.wav', sound_path)

def play_power_up_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/power-up1.wav', sound_path)

def play_purchase_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/purchase1.wav', sound_path)

def play_project_finished_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/project-finished1.wav', sound_path) 

def play_job_arrived_sound(sound_path=None):
    play_sound_effect('data/audio/sounds/job-arrived1.wav', sound_path)
