from modules import analyze_audio
import json

audio_file = 'test_files/tts2/6.wav'
name = audio_file.split("/")[-1].split(".")[0]
result = analyze_audio(audio_file)

result_dicts = [{"time": time, "amplitude": amp, "status": status if status else "None"} for time, amp, status in result]
result_json_file = f'results/result_{name}.json'

with open(result_json_file, 'w') as f:
    json.dump(result_dicts, f, indent=4)

print(f"Saved 'result' to {result_json_file}")


