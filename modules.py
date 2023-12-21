import parselmouth
import numpy as np

def analyze_formants(audio_path):
    sound = parselmouth.Sound(audio_path)
    formant = sound.to_formant_burg()
    formant_data = []

    for t in formant.t_grid():
        f1 = formant.get_value_at_time(1, t)
        f2 = formant.get_value_at_time(2, t)
        if np.isnan(f1) or np.isnan(f2):
            continue
        formant_data.append((t, f1, f2))

    return formant_data

def map_to_vowel(f1, f2):
    vowels = {
        "/i/": (270, 2290),
        "/e/": (530, 1840),
        "/a/": (660, 1720),
        "/o/": (570, 840),
        "/u/": (300, 870),
        # Add more vowels as needed
    }

    closest_vowel = None
    smallest_distance = float('inf')

    for vowel, (ref_f1, ref_f2) in vowels.items():
        distance = np.sqrt((ref_f1 - f1)**2 + (ref_f2 - f2)**2)
        if distance < smallest_distance:
            smallest_distance = distance
            closest_vowel = vowel

    return closest_vowel, smallest_distance

def recognize_vowels(audio_path, threshold=150):
    formants = analyze_formants(audio_path)
    vowel_occurrences = []

    for time, f1, f2 in formants:
        vowel, distance = map_to_vowel(f1, f2)
        if distance <= threshold:
            vowel_occurrences.append((time, vowel))

    return vowel_occurrences

# Example usage
audio_file = "/avir_checkpoint_878000.wav"
vowels_detected = recognize_vowels(audio_file)
for time, vowel in vowels_detected:
    print(f"Time: {time:.3f} s, Vowel: {vowel}")
