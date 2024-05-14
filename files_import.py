from PyQt5.QtWidgets import QFileDialog
import mido
import plots as pl
from mido import Message, MidiFile, MidiTrack
import threading
import time as tt

#Definir constantes
PIANO_BOX = 1
GUITAR_BOX = 2




def import_track_files(self, i):
    filename = QFileDialog.getOpenFileName(self, 'Open File', 'c:\\', 'Track Files (*.mid *.midi)')
    print(filename[0])
    if filename[0]:
        if i == 1:
            self.track_data.track_1_filename = filename[0]
        elif i == 2:
            self.track_data.track_2_filename = filename[0]
        elif i == 3:
            self.track_data.track_3_filename = filename[0]
    notes_proccessing(self, i)
    

def leer_archivo_midi(ruta_archivo):
    try:
        mid = pretty_midi.PrettyMIDI(ruta_archivo)
        return mid
    except Exception as e:
        print("Error al leer el archivo MIDI:", e)
        return None

def dividir_pistas(mid, canal_deseado):
    return mid.instruments[canal_deseado].notes


def notes_proccessing(self, i):
    # node_filenames = [self.track_data.track_1_filename, self.track_data.track_2_mid, self.track_data.track_3_mid]
    # node_box = [self.channel_1_box.value(), self.channel_2_box.value(), self.channel_3_box.value()]
    node_filenames = [self.track_data.track_1_filename, self.track_data.track_2_filename, self.track_data.track_3_filename]
    node_box = [self.channel_1_box.value(), self.channel_2_box.value(), self.channel_3_box.value()]
    node_mid = [self.track_data.track_1_mid, self.track_data.track_2_mid, self.track_data.track_3_mid]
    node_samples = [self.track_data.track_1_samples, self.track_data.track_2_samples, self.track_data.track_3_samples]
    
    if node_filenames[i-1] != []:
        mid = leer_archivo_midi(  node_filenames[i-1] )
        if mid is not None:
            mid_data = dividir_pistas(mid, int(node_box[i-1]))
            if i == 1:
                self.track_data.track_1_mid = mid_data
            elif i == 2:
                self.track_data.track_2_mid = mid_data
            elif i == 3:
                self.track_data.track_3_mid = mid_data
            
                        
        
            
            
            
def synth_data(self, i):
    node_ins_box = [self.track_1_box.currentIndex(), self.track_2_box.currentIndex(), self.track_3_box.currentIndex()]

    if(node_ins_box[i-1] == PIANO_BOX):
        print("Sintetizando piano")
        if (i == 1):
            self.track_data.track_1_samples = synthesis_piano(self.track_data.track_1_mid)
        elif (i == 2):
            self.track_data.track_2_samples = synthesis_piano(self.track_data.track_2_mid)
        elif (i == 3):
            self.track_data.track_3_samples = synthesis_piano(self.track_data.track_3_mid)
        print("Sintetizacion finalizada")
    elif(node_ins_box[i-1] == GUITAR_BOX):
        print("Sintetizando guitarra")                


def plot_data(self, i):
    if i == 1:
        mid_data = self.track_data.track_1_mid
    elif i == 2:
        mid_data = self.track_data.track_2_mid
    elif i == 3:
        mid_data = self.track_data.track_3_mid
        
    pl.plot_scatter(mid_data, self, i)
    pl.plot_temporal(mid_data, self, i)
    pl.plot_spectrogram(mid_data, self, i)
            
        
        
        
import threading
import mido
from mido import MidiFile, MidiTrack, Message
import sounddevice as sd

# Variable global para controlar la reproducción
stop_playing = False

def thread_play_midi(self, i):
    node_samples = [self.track_data.track_1_samples, self.track_data.track_2_samples, self.track_data.track_3_samples]
    samples = node_samples[i-1]
    global stop_playing
    stop_playing = False
    midi_thread = threading.Thread(target=play_midi, args=(samples, ))
    midi_thread.start()

def stop_playback():
    print("Stopping playback")
    global stop_playing
    stop_playing = True
    sd.stop()
    
    
def play_midi(samples):
    if len(samples) != 0:
        while not stop_playing:
            print("Playing MIDI")
            sd.play(samples, 44100)
            sd.wait()
            print("Playback finished")
            stop_playback()


import numpy as np
import pretty_midi
from sample_synth import sample_synthesis

sample_rate = 44100

def get_notes_from_track(track):
    notes = []
    for note in track:
        notes.append({
            'pitch': note.pitch,
            'start': note.start,
            'end': note.end,
            'velocity': note.velocity,
            'synth': []
        })
    return notes

def synthesis_piano (track):
    track_notes = get_notes_from_track(track)
    
    min_pitch = min(note['pitch'] for note in track_notes)
    max_pitch = max(note['pitch'] for note in track_notes)
    max_end = max(note['end'] for note in track_notes)

    for note in track_notes:
        note['synth'] = sample_synthesis(note['pitch'],  note['velocity'], note['end'] - note['start'])

    num_pitches = max_pitch - min_pitch + 1
    num_samples = int(np.ceil(max_end))*sample_rate
    tracks_s = np.zeros((num_pitches, num_samples))

    for note in track_notes:
        pitch = note['pitch'] - min_pitch
        start_frame = round(note['start']*sample_rate)
        # end_frame = int(np.ceil(note['end']*sample_rate))
        end_frame = start_frame + len(note['synth'])
        tracks_s[pitch, start_frame:end_frame] = note['synth']

    return np.sum(tracks_s, axis=0)