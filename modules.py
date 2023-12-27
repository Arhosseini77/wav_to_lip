import parselmouth
import numpy as np


def analyze_formants_and_intensity(audio_path):
    sound = parselmouth.Sound(audio_path)
    formant = sound.to_formant_burg()
    intensity = sound.to_intensity()
    analysis_data = []

    # Extract intensity times and values, ensuring they are one-dimensional
    intensity_times = intensity.xs()
    intensity_values = intensity.values.flatten()  # Flatten to ensure 1D array

    for t in formant.t_grid():
        f1 = formant.get_value_at_time(1, t)
        f2 = formant.get_value_at_time(2, t)

        # Find the index of the closest time in intensity_times to t
        closest_time_index = np.abs(intensity_times - t).argmin()
        # Ensure index is within bounds
        if closest_time_index < len(intensity_values):
            intensity_at_t = intensity_values[closest_time_index]
        else:
            continue

        if np.isnan(f1) or np.isnan(f2):
            continue
        analysis_data.append((t, f1, f2, intensity_at_t))

    return analysis_data


def get_amplitude_value(audio_path):
    sound = parselmouth.Sound(audio_path)
    intensity = sound.to_intensity()
    rms = np.sqrt(np.mean(intensity.values**2))
    max_possible_rms = 1.0  # Adjust based on your audio format
    normalized_rms = rms / max_possible_rms
    return min(max(normalized_rms, 0), 1)


def is_silent(intensity, silence_threshold=50):
    return intensity < silence_threshold


def map_to_vowel(f1, f2):
    vowels = {
        "long_ee": (280, 2230),   # [i] like "team"
        "short_ee": (370, 2090),  # [ɪ] like "ear"
        "short_e": (405, 2080),   # [e] like "hair"
        "long_e": (600, 1930),    # [ɛ] like "Turn"
        "short_aa": (860, 1550),  # [æ] like "Cat"
        "long_aa": (830, 1170),   # [ɑ] like "Fast"
        "long_a": (560, 820),     # [ɔ] like "Talk"
        "short_ou": (400, 1100),  # [ʊ] like put
        "long_ou": (330, 1260),   # [u] like "boot"
        "short_a": (680, 1310),   # [ʌ] like "Fun"
    }

    closest_vowel = None
    smallest_distance = float('inf')

    for vowel, (ref_f1, ref_f2) in vowels.items():
        distance = np.sqrt((ref_f1 - f1)**2 + (ref_f2 - f2)**2)
        if distance < smallest_distance:
            smallest_distance = distance
            closest_vowel = vowel

    return closest_vowel, smallest_distance


def analyze_audio(audio_path):
    analysis_data = analyze_formants_and_intensity(audio_path)
    result = []
    last_five_entries = []
    repeat_count = 0

    for time, f1, f2, intensity in analysis_data:
        # Normalize intensity: Map 50 to 0 and 100 to 1
        normalized_intensity = (intensity - 50) / 50
        normalized_intensity = min(max(normalized_intensity, 0), 1)
        # Check for silence or vowel and prepare output tuple
        if is_silent(normalized_intensity * 100, silence_threshold=0):
            current_entry = (time, 0, "Silent")
            last_vowel = None
            repeat_count = 0
        else:
            if repeat_count > 0:
                current_entry = (time, normalized_intensity, last_vowel)
                repeat_count -= 1
            else:
                vowel, distance = map_to_vowel(f1, f2)
                if distance <= 50:  # Threshold for vowel detection
                    current_entry = (time, normalized_intensity, vowel)
                    last_vowel = vowel
                    repeat_count = 5

                    # Overwrite the last five entries if a vowel is detected
                    for i in range(len(last_five_entries)):
                        if last_five_entries[i][2] != "Silent":
                            last_five_entries[i] = (last_five_entries[i][0], last_five_entries[i][1], vowel)
                else:
                    current_entry = (time, normalized_intensity, None)
                    last_vowel = None

            # Update the result and the last_five_entries buffer
        last_five_entries.append(current_entry)
        if len(last_five_entries) > 5:
            result.append(last_five_entries.pop(0))
        else:
            result.append(current_entry)

        # Add any remaining entries from the buffer to the result
    result.extend(last_five_entries[1:])

    return result