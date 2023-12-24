from modules import analyze_audio

audio_file = 'test_files/only_silent.mp3'
result = analyze_audio(audio_file)
for res in result:
    print(res)