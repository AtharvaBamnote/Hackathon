"""
Text-to-Speech module using Coqui TTS with phoneme extraction.
Supports multilingual speech synthesis and phoneme alignment.
"""

import os
import torch
import librosa
import numpy as np
import soundfile as sf
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from phonemizer import phonemize
from typing import List, Tuple, Dict
import tempfile
import json


class TextToSpeech:
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        """
        Initialize TTS with Coqui TTS model.
        
        Args:
            model_name: TTS model name
        """
        self.model_name = model_name
        self.tts = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load the TTS model."""
        try:
            print(f"Loading TTS model: {self.model_name}")
            self.tts = TTS(model_name=self.model_name).to(self.device)
            print("TTS model loaded successfully!")
        except Exception as e:
            print(f"Error loading TTS model: {e}")
            print("Falling back to basic TTS model...")
            try:
                # Fallback to a simpler model
                self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC").to(self.device)
                print("Fallback TTS model loaded!")
            except Exception as e2:
                print(f"Failed to load fallback model: {e2}")
    
    def synthesize_speech(self, text: str, language: str = "en", output_path: str = None) -> str:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            language: Language code ('en' for English, 'hi' for Hindi)
            output_path: Output audio file path
            
        Returns:
            Path to generated audio file
        """
        if not self.tts:
            print("TTS model not loaded")
            return None
        
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav")
        
        try:
            # Map language codes
            lang_map = {
                'en': 'en',
                'hi': 'hi',
                'default': 'en'
            }
            tts_lang = lang_map.get(language, 'en')
            
            # Generate speech
            if hasattr(self.tts, 'tts_to_file'):
                # For models that support direct file output
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language=tts_lang
                )
            else:
                # For models that return audio array
                wav = self.tts.tts(text=text, language=tts_lang)
                sf.write(output_path, wav, 22050)
            
            print(f"Speech synthesized: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error synthesizing speech: {e}")
            # Create a simple fallback audio file
            try:
                # Generate simple sine wave as fallback
                duration = len(text) * 0.1  # Rough estimate
                sample_rate = 22050
                t = np.linspace(0, duration, int(sample_rate * duration))
                frequency = 440  # A4 note
                audio = 0.3 * np.sin(2 * np.pi * frequency * t)
                sf.write(output_path, audio, sample_rate)
                return output_path
            except:
                return None
    
    def extract_phonemes(self, text: str, language: str = "en") -> List[str]:
        """
        Extract phonemes from text.
        
        Args:
            text: Input text
            language: Language code
            
        Returns:
            List of phonemes
        """
        try:
            # Map language codes for phonemizer
            lang_map = {
                'en': 'en-us',
                'hi': 'hi',  # May need adjustment based on available languages
                'default': 'en-us'
            }
            phonemizer_lang = lang_map.get(language, 'en-us')
            
            # Extract phonemes using phonemizer
            phonemes = phonemize(
                text,
                language=phonemizer_lang,
                backend='espeak',
                separator=phonemizer.separator.Separator(phone=' '),
                strip=True,
                preserve_punctuation=False,
                with_stress=False
            )
            
            # Split into individual phonemes
            phoneme_list = phonemes.split()
            
            # Clean up phonemes (remove special characters)
            cleaned_phonemes = []
            for phoneme in phoneme_list:
                cleaned = phoneme.strip('ˈˌ')  # Remove stress markers
                if cleaned and cleaned not in [' ', '']:
                    cleaned_phonemes.append(cleaned)
            
            return cleaned_phonemes
            
        except Exception as e:
            print(f"Error extracting phonemes: {e}")
            # Fallback: create simple phoneme mapping
            return self._simple_phoneme_mapping(text)
    
    def _simple_phoneme_mapping(self, text: str) -> List[str]:
        """
        Simple fallback phoneme mapping when phonemizer fails.
        
        Args:
            text: Input text
            
        Returns:
            List of approximate phonemes
        """
        # Very basic mapping for common letters/sounds
        phoneme_map = {
            'a': 'ə', 'e': 'ɛ', 'i': 'ɪ', 'o': 'ɔ', 'u': 'ʊ',
            'b': 'b', 'c': 'k', 'd': 'd', 'f': 'f', 'g': 'g',
            'h': 'h', 'j': 'dʒ', 'k': 'k', 'l': 'l', 'm': 'm',
            'n': 'n', 'p': 'p', 'q': 'k', 'r': 'r', 's': 's',
            't': 't', 'v': 'v', 'w': 'w', 'x': 'ks', 'y': 'j', 'z': 'z'
        }
        
        phonemes = []
        for char in text.lower():
            if char.isalpha():
                phonemes.append(phoneme_map.get(char, char))
        
        return phonemes
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            audio, sr = librosa.load(audio_path)
            return len(audio) / sr
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 0.0
    
    def align_phonemes_to_audio(self, phonemes: List[str], audio_duration: float) -> List[Dict]:
        """
        Align phonemes to audio timeline (simplified version).
        
        Args:
            phonemes: List of phonemes
            audio_duration: Audio duration in seconds
            
        Returns:
            List of phoneme timing information
        """
        if not phonemes:
            return []
        
        # Simple equal distribution of phonemes over audio duration
        phoneme_duration = audio_duration / len(phonemes)
        
        aligned_phonemes = []
        current_time = 0.0
        
        for phoneme in phonemes:
            aligned_phonemes.append({
                "phoneme": phoneme,
                "start_time": current_time,
                "end_time": current_time + phoneme_duration,
                "duration": phoneme_duration
            })
            current_time += phoneme_duration
        
        return aligned_phonemes
    
    def generate_speech_with_phonemes(self, text: str, language: str = "en") -> Tuple[str, List[Dict]]:
        """
        Generate speech and extract aligned phonemes.
        
        Args:
            text: Text to synthesize
            language: Language code
            
        Returns:
            Tuple of (audio_file_path, aligned_phonemes)
        """
        # Synthesize speech
        audio_path = self.synthesize_speech(text, language)
        if not audio_path:
            return None, []
        
        # Extract phonemes
        phonemes = self.extract_phonemes(text, language)
        
        # Get audio duration
        duration = self.get_audio_duration(audio_path)
        
        # Align phonemes to audio
        aligned_phonemes = self.align_phonemes_to_audio(phonemes, duration)
        
        return audio_path, aligned_phonemes


class SimpleTTSFallback:
    """
    Simple fallback TTS using system speech synthesis.
    Used when Coqui TTS is not available.
    """
    
    def __init__(self):
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if system TTS is available."""
        try:
            import subprocess
            # Try to use espeak or say command
            result = subprocess.run(['which', 'espeak'], capture_output=True)
            if result.returncode == 0:
                self.tts_command = 'espeak'
                return True
            
            result = subprocess.run(['which', 'say'], capture_output=True)
            if result.returncode == 0:
                self.tts_command = 'say'
                return True
            
            return False
        except:
            return False
    
    def synthesize_speech(self, text: str, language: str = "en", output_path: str = None) -> str:
        """Simple speech synthesis using system commands."""
        if not self.available:
            return None
        
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav")
        
        try:
            import subprocess
            
            if self.tts_command == 'espeak':
                cmd = ['espeak', '-w', output_path, text]
            elif self.tts_command == 'say':
                cmd = ['say', '-o', output_path, text]
            else:
                return None
            
            subprocess.run(cmd, check=True)
            return output_path
            
        except Exception as e:
            print(f"Error with system TTS: {e}")
            return None


def test_tts():
    """Test function for TTS."""
    print("Testing Text-to-Speech...")
    
    # Try main TTS
    tts = TextToSpeech()
    
    test_texts = [
        ("Hello, this is a test of the text-to-speech system!", "en"),
        ("नमस्ते, यह टेक्स्ट-टू-स्पीच सिस्टम का परीक्षण है!", "hi")
    ]
    
    for text, lang in test_texts:
        print(f"\nTesting ({lang}): {text}")
        
        # Generate speech with phonemes
        audio_path, phonemes = tts.generate_speech_with_phonemes(text, lang)
        
        if audio_path:
            print(f"Audio generated: {audio_path}")
            print(f"Phonemes extracted: {len(phonemes)} phonemes")
            for i, phoneme_info in enumerate(phonemes[:5]):  # Show first 5
                print(f"  {i+1}. {phoneme_info}")
        else:
            print("Failed to generate audio")
    
    print("\nTTS module ready!")


if __name__ == "__main__":
    test_tts()