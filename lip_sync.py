"""
Lip-sync module for mapping phonemes to visemes.
Converts phoneme timeline to viseme timeline for 3D avatar animation.
"""

import json
from typing import List, Dict, Tuple
import numpy as np


class LipSyncProcessor:
    def __init__(self):
        """Initialize lip-sync processor with phoneme-to-viseme mapping."""
        self.phoneme_to_viseme = self._create_phoneme_viseme_mapping()
        self.viseme_descriptions = self._create_viseme_descriptions()
    
    def _create_phoneme_viseme_mapping(self) -> Dict[str, str]:
        """
        Create mapping from phonemes to visemes.
        Based on standard viseme sets used in 3D animation.
        """
        return {
            # Silence
            'sil': 'X',
            'sp': 'X',
            '': 'X',
            
            # Vowels
            'a': 'A',      # "father" - open mouth
            'ə': 'A',      # "about" - neutral vowel
            'æ': 'A',      # "cat" - open mouth
            'e': 'E',      # "bed" - mid front vowel
            'ɛ': 'E',      # "bet" - open-mid front
            'i': 'I',      # "see" - close front vowel
            'ɪ': 'I',      # "sit" - near-close front
            'o': 'O',      # "go" - close-mid back vowel
            'ɔ': 'O',      # "thought" - open-mid back
            'u': 'U',      # "food" - close back vowel
            'ʊ': 'U',      # "foot" - near-close back
            'ʌ': 'A',      # "cup" - open-mid back
            
            # Consonants - Bilabials (lip sounds)
            'p': 'P',      # "pat" - lips together
            'b': 'P',      # "bat" - lips together
            'm': 'P',      # "mat" - lips together
            
            # Labiodentals (lip-teeth)
            'f': 'F',      # "fat" - lower lip to upper teeth
            'v': 'F',      # "vat" - lower lip to upper teeth
            
            # Dental/Alveolar
            't': 'T',      # "top" - tongue tip
            'd': 'T',      # "dog" - tongue tip
            'n': 'T',      # "not" - tongue tip
            's': 'S',      # "sit" - tongue groove
            'z': 'S',      # "zip" - tongue groove
            'l': 'L',      # "let" - tongue lateral
            'r': 'R',      # "red" - tongue retroflex
            
            # Postalveolar
            'ʃ': 'S',      # "she" - tongue blade raised
            'ʒ': 'S',      # "measure" - tongue blade raised
            'tʃ': 'S',     # "church" - tongue blade
            'dʒ': 'S',     # "judge" - tongue blade
            
            # Velar
            'k': 'K',      # "cat" - tongue back
            'g': 'K',      # "go" - tongue back
            'ŋ': 'K',      # "sing" - tongue back
            
            # Glottal
            'h': 'A',      # "hat" - open
            
            # Approximants
            'w': 'W',      # "we" - rounded lips
            'j': 'I',      # "yes" - close front
            
            # Vowel-like
            'aɪ': 'A',     # "my" - diphthong
            'aʊ': 'A',     # "now" - diphthong
            'eɪ': 'E',     # "day" - diphthong
            'oʊ': 'O',     # "go" - diphthong
            'ɔɪ': 'O',     # "boy" - diphthong
        }
    
    def _create_viseme_descriptions(self) -> Dict[str, Dict]:
        """
        Create descriptions for each viseme with mouth shape parameters.
        These can be used to drive 3D facial animation.
        """
        return {
            'X': {  # Silence
                'name': 'silence',
                'mouth_open': 0.0,
                'mouth_width': 0.5,
                'lip_pucker': 0.0,
                'description': 'Mouth closed, neutral position'
            },
            'A': {  # Open vowels
                'name': 'open',
                'mouth_open': 0.8,
                'mouth_width': 0.6,
                'lip_pucker': 0.0,
                'description': 'Mouth open, like "ah"'
            },
            'E': {  # Mid vowels
                'name': 'mid',
                'mouth_open': 0.4,
                'mouth_width': 0.7,
                'lip_pucker': 0.0,
                'description': 'Mouth slightly open, like "eh"'
            },
            'I': {  # Close front vowels
                'name': 'close',
                'mouth_open': 0.2,
                'mouth_width': 0.8,
                'lip_pucker': 0.0,
                'description': 'Mouth narrow, like "ee"'
            },
            'O': {  # Back vowels
                'name': 'back',
                'mouth_open': 0.5,
                'mouth_width': 0.4,
                'lip_pucker': 0.3,
                'description': 'Mouth round, like "oh"'
            },
            'U': {  # Close back vowels
                'name': 'round',
                'mouth_open': 0.3,
                'mouth_width': 0.3,
                'lip_pucker': 0.6,
                'description': 'Lips rounded, like "oo"'
            },
            'P': {  # Bilabial consonants
                'name': 'bilabial',
                'mouth_open': 0.0,
                'mouth_width': 0.5,
                'lip_pucker': 0.0,
                'description': 'Lips together, like "p", "b", "m"'
            },
            'F': {  # Labiodental consonants
                'name': 'labiodental',
                'mouth_open': 0.1,
                'mouth_width': 0.6,
                'lip_pucker': 0.0,
                'description': 'Lower lip to upper teeth, like "f", "v"'
            },
            'T': {  # Tongue tip consonants
                'name': 'tongue_tip',
                'mouth_open': 0.2,
                'mouth_width': 0.6,
                'lip_pucker': 0.0,
                'description': 'Tongue tip active, like "t", "d", "n"'
            },
            'S': {  # Sibilant consonants
                'name': 'sibilant',
                'mouth_open': 0.1,
                'mouth_width': 0.7,
                'lip_pucker': 0.0,
                'description': 'Tongue groove, like "s", "sh"'
            },
            'L': {  # Lateral consonants
                'name': 'lateral',
                'mouth_open': 0.3,
                'mouth_width': 0.6,
                'lip_pucker': 0.0,
                'description': 'Tongue lateral, like "l"'
            },
            'R': {  # Rhotic consonants
                'name': 'rhotic',
                'mouth_open': 0.3,
                'mouth_width': 0.5,
                'lip_pucker': 0.2,
                'description': 'Tongue retroflex, like "r"'
            },
            'K': {  # Velar consonants
                'name': 'velar',
                'mouth_open': 0.2,
                'mouth_width': 0.5,
                'lip_pucker': 0.0,
                'description': 'Tongue back, like "k", "g"'
            },
            'W': {  # Approximant w
                'name': 'approximant',
                'mouth_open': 0.2,
                'mouth_width': 0.3,
                'lip_pucker': 0.5,
                'description': 'Rounded lips, like "w"'
            }
        }
    
    def phonemes_to_visemes(self, phoneme_timeline: List[Dict]) -> List[Dict]:
        """
        Convert phoneme timeline to viseme timeline.
        
        Args:
            phoneme_timeline: List of phoneme timing dictionaries
                             Format: [{'phoneme': 'p', 'start_time': 0.0, 'end_time': 0.1}, ...]
        
        Returns:
            List of viseme timing dictionaries
            Format: [{'time': 0.0, 'viseme': 'P', 'duration': 0.1, 'parameters': {...}}, ...]
        """
        if not phoneme_timeline:
            return []
        
        viseme_timeline = []
        
        for phoneme_info in phoneme_timeline:
            phoneme = phoneme_info.get('phoneme', '')
            start_time = phoneme_info.get('start_time', 0.0)
            end_time = phoneme_info.get('end_time', 0.0)
            duration = end_time - start_time
            
            # Map phoneme to viseme
            viseme = self.phoneme_to_viseme.get(phoneme, 'X')
            
            # Get viseme parameters
            parameters = self.viseme_descriptions.get(viseme, self.viseme_descriptions['X'])
            
            viseme_entry = {
                'time': start_time,
                'viseme': viseme,
                'duration': duration,
                'parameters': {
                    'mouth_open': parameters['mouth_open'],
                    'mouth_width': parameters['mouth_width'],
                    'lip_pucker': parameters['lip_pucker']
                },
                'description': parameters['description'],
                'original_phoneme': phoneme
            }
            
            viseme_timeline.append(viseme_entry)
        
        return viseme_timeline
    
    def smooth_viseme_transitions(self, viseme_timeline: List[Dict], smoothing_factor: float = 0.1) -> List[Dict]:
        """
        Smooth transitions between visemes for more natural animation.
        
        Args:
            viseme_timeline: List of viseme timing dictionaries
            smoothing_factor: Amount of smoothing (0.0 = no smoothing, 1.0 = maximum)
        
        Returns:
            Smoothed viseme timeline
        """
        if len(viseme_timeline) < 2:
            return viseme_timeline
        
        smoothed_timeline = []
        
        for i, current_viseme in enumerate(viseme_timeline):
            smoothed_viseme = current_viseme.copy()
            
            # Apply smoothing with neighboring visemes
            if i > 0 and i < len(viseme_timeline) - 1:
                prev_params = viseme_timeline[i-1]['parameters']
                next_params = viseme_timeline[i+1]['parameters']
                current_params = current_viseme['parameters']
                
                # Smooth each parameter
                for param in ['mouth_open', 'mouth_width', 'lip_pucker']:
                    prev_val = prev_params[param]
                    current_val = current_params[param]
                    next_val = next_params[param]
                    
                    # Apply weighted average
                    smoothed_val = (
                        prev_val * smoothing_factor * 0.5 +
                        current_val * (1 - smoothing_factor) +
                        next_val * smoothing_factor * 0.5
                    )
                    
                    smoothed_viseme['parameters'][param] = smoothed_val
            
            smoothed_timeline.append(smoothed_viseme)
        
        return smoothed_timeline
    
    def create_keyframe_animation(self, viseme_timeline: List[Dict]) -> Dict:
        """
        Create keyframe animation data for 3D avatar.
        
        Args:
            viseme_timeline: List of viseme timing dictionaries
        
        Returns:
            Animation data suitable for Three.js or Unity
        """
        animation_data = {
            'name': 'lip_sync_animation',
            'duration': viseme_timeline[-1]['time'] + viseme_timeline[-1]['duration'] if viseme_timeline else 0,
            'tracks': []
        }
        
        # Create separate tracks for each facial parameter
        parameters = ['mouth_open', 'mouth_width', 'lip_pucker']
        
        for param in parameters:
            track = {
                'name': f'facial.{param}',
                'type': 'number',
                'times': [],
                'values': []
            }
            
            for viseme in viseme_timeline:
                track['times'].append(viseme['time'])
                track['values'].append(viseme['parameters'][param])
            
            animation_data['tracks'].append(track)
        
        # Add viseme name track for debugging/reference
        viseme_track = {
            'name': 'viseme_names',
            'type': 'string',
            'times': [],
            'values': []
        }
        
        for viseme in viseme_timeline:
            viseme_track['times'].append(viseme['time'])
            viseme_track['values'].append(viseme['viseme'])
        
        animation_data['tracks'].append(viseme_track)
        
        return animation_data
    
    def export_for_threejs(self, viseme_timeline: List[Dict]) -> str:
        """
        Export viseme timeline in format suitable for Three.js.
        
        Args:
            viseme_timeline: List of viseme timing dictionaries
        
        Returns:
            JSON string for Three.js animation
        """
        animation_data = self.create_keyframe_animation(viseme_timeline)
        return json.dumps(animation_data, indent=2)
    
    def export_for_unity(self, viseme_timeline: List[Dict]) -> str:
        """
        Export viseme timeline in format suitable for Unity.
        
        Args:
            viseme_timeline: List of viseme timing dictionaries
        
        Returns:
            JSON string for Unity animation
        """
        unity_data = {
            'clip_name': 'LipSyncClip',
            'length': viseme_timeline[-1]['time'] + viseme_timeline[-1]['duration'] if viseme_timeline else 0,
            'curves': [],
            'events': []
        }
        
        # Create animation curves
        parameters = ['mouth_open', 'mouth_width', 'lip_pucker']
        
        for param in parameters:
            curve = {
                'path': f'facial_{param}',
                'attribute': 'localScale.x' if param == 'mouth_width' else 'localPosition.y',
                'keyframes': []
            }
            
            for viseme in viseme_timeline:
                keyframe = {
                    'time': viseme['time'],
                    'value': viseme['parameters'][param],
                    'in_tangent': 0,
                    'out_tangent': 0
                }
                curve['keyframes'].append(keyframe)
            
            unity_data['curves'].append(curve)
        
        # Add viseme change events
        for viseme in viseme_timeline:
            event = {
                'time': viseme['time'],
                'function_name': 'OnVisemeChange',
                'string_parameter': viseme['viseme'],
                'float_parameter': viseme['duration']
            }
            unity_data['events'].append(event)
        
        return json.dumps(unity_data, indent=2)


def test_lip_sync():
    """Test function for lip-sync processor."""
    print("Testing Lip-Sync Processor...")
    
    lip_sync = LipSyncProcessor()
    
    # Sample phoneme timeline (from TTS output)
    sample_phonemes = [
        {'phoneme': 'h', 'start_time': 0.0, 'end_time': 0.1},
        {'phoneme': 'ə', 'start_time': 0.1, 'end_time': 0.2},
        {'phoneme': 'l', 'start_time': 0.2, 'end_time': 0.3},
        {'phoneme': 'oʊ', 'start_time': 0.3, 'end_time': 0.5},
        {'phoneme': 'sil', 'start_time': 0.5, 'end_time': 0.6},
        {'phoneme': 'w', 'start_time': 0.6, 'end_time': 0.7},
        {'phoneme': 'ɜ', 'start_time': 0.7, 'end_time': 0.8},
        {'phoneme': 'l', 'start_time': 0.8, 'end_time': 0.9},
        {'phoneme': 'd', 'start_time': 0.9, 'end_time': 1.0}
    ]
    
    print(f"Input phonemes: {len(sample_phonemes)}")
    for phoneme in sample_phonemes:
        print(f"  {phoneme['phoneme']} ({phoneme['start_time']:.1f}s - {phoneme['end_time']:.1f}s)")
    
    # Convert to visemes
    viseme_timeline = lip_sync.phonemes_to_visemes(sample_phonemes)
    
    print(f"\nOutput visemes: {len(viseme_timeline)}")
    for viseme in viseme_timeline:
        print(f"  {viseme['viseme']} at {viseme['time']:.1f}s - {viseme['description']}")
    
    # Apply smoothing
    smoothed_timeline = lip_sync.smooth_viseme_transitions(viseme_timeline)
    
    # Export for Three.js
    threejs_data = lip_sync.export_for_threejs(smoothed_timeline)
    print(f"\nThree.js export (first 200 chars):\n{threejs_data[:200]}...")
    
    # Save example JSON
    with open('/workspace/example_viseme_timeline.json', 'w') as f:
        json.dump(smoothed_timeline, f, indent=2)
    
    print(f"\nExample viseme timeline saved to: example_viseme_timeline.json")
    print("Lip-Sync module ready!")


if __name__ == "__main__":
    test_lip_sync()