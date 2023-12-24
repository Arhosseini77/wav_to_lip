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
        "[i]": (280, 2230),
        "[ɪ]": (370, 2090),
        "[e]": (405, 2080),
        "[ɛ]": (600, 1930),
        "[æ]": (860, 1550),
        "[ɑ]": (830, 1170),
        "[ɔ]": (560, 820),
        "[o]": (430, 980),
        "[ʊ]": (400, 1100),
        "[u]": (330, 1260),
        "[ʌ]": (680, 1310),
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

    for time, f1, f2, intensity in analysis_data:
        # Normalize intensity: Map 50 to 0 and 100 to 1
        normalized_intensity = (intensity - 50) / 50
        normalized_intensity = min(max(normalized_intensity, 0), 1)

        # Check for silence or vowel and prepare output tuple
        if is_silent(normalized_intensity * 100, silence_threshold=50):  # Use original scale for silence check
            result.append((time, normalized_intensity, "Silent"))
        else:
            vowel, distance = map_to_vowel(f1, f2)
            if distance <= 50:  # Threshold for vowel detection
                result.append((time, normalized_intensity, vowel))
            else:
                result.append((time, normalized_intensity, None))

    return result