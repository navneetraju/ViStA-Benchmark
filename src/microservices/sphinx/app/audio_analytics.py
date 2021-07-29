import os, shutil 
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
import moviepy.editor as mp 
from time import sleep

r = sr.Recognizer()

def get_large_audio_transcription(path_to_storage, video_name):
    movie_name = video_name.split('.')[0]
    path_to_video = os.path.join(path_to_storage, video_name)
    clip = mp.VideoFileClip(path_to_video)
    print('1')
    audio_path= os.path.join(path_to_storage, movie_name+".wav")
    clip.audio.write_audiofile(audio_path)
    print('2')
    sound = AudioSegment.from_wav(audio_path)  
    chunks = split_on_silence(sound,
        min_silence_len = 500,
        silence_thresh = sound.dBFS-14,
        keep_silence=500,
    )
    folder_name = movie_name+"_audio"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            try:
                text = r.recognize_sphinx(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    if os.path.isfile(audio_path):
        os.remove(audio_path)
    if os.path.isdir(folder_name):
        shutil.rmtree(folder_name)
    return whole_text
