"""
Multilingual chatbot engine with rule-based responses.
Supports English and Hindi conversations with emotion detection.
"""

import re
import random
from typing import Dict, List, Tuple
from langdetect import detect
import json


class MultilingualChatbot:
    def __init__(self):
        """Initialize the chatbot with multilingual responses."""
        self.responses = self._load_responses()
        self.emotion_keywords = self._load_emotion_keywords()
        self.conversation_history = []
    
    def _load_responses(self) -> Dict:
        """Load response templates for different languages and intents."""
        return {
            "greetings": {
                "en": [
                    "Hello! How can I help you today?",
                    "Hi there! What would you like to talk about?",
                    "Greetings! I'm here to chat with you."
                ],
                "hi": [
                    "नमस्ते! आज मैं आपकी कैसे सहायता कर सकूं?",
                    "हैलो! आप किस बारे में बात करना चाहते हैं?",
                    "नमस्कार! मैं आपसे बात करने के लिए यहाँ हूँ।"
                ]
            },
            "how_are_you": {
                "en": [
                    "I'm doing great, thank you for asking! How are you?",
                    "I'm wonderful! Thanks for asking. How about you?",
                    "I'm excellent! How has your day been?"
                ],
                "hi": [
                    "मैं बहुत अच्छा हूँ, पूछने के लिए धन्यवाद! आप कैसे हैं?",
                    "मैं बहुत खुश हूँ! पूछने के लिए धन्यवाद। आप कैसे हैं?",
                    "मैं शानदार हूँ! आपका दिन कैसा रहा?"
                ]
            },
            "goodbye": {
                "en": [
                    "Goodbye! It was nice talking to you!",
                    "See you later! Take care!",
                    "Bye! Have a wonderful day!"
                ],
                "hi": [
                    "अलविदा! आपसे बात करके अच्छा लगा!",
                    "फिर मिलेंगे! अपना ख्याल रखें!",
                    "बाय! आपका दिन शुभ हो!"
                ]
            },
            "help": {
                "en": [
                    "I can help you with conversations in English and Hindi!",
                    "I'm here to chat and answer your questions!",
                    "Feel free to ask me anything - I speak both English and Hindi!"
                ],
                "hi": [
                    "मैं अंग्रेजी और हिंदी में बातचीत में आपकी मदद कर सकूं!",
                    "मैं यहाँ चैट करने और आपके सवालों के जवाब देने के लिए हूँ!",
                    "मुझसे कुछ भी पूछने में संकोच न करें - मैं अंग्रेजी और हिंदी दोनों बोलता हूँ!"
                ]
            },
            "weather": {
                "en": [
                    "I can't check the weather right now, but I hope it's nice where you are!",
                    "Weather is always a good topic! How's the weather in your area?",
                    "I'd love to tell you about the weather, but I don't have access to that data right now."
                ],
                "hi": [
                    "मैं अभी मौसम की जांच नहीं कर सकता, लेकिन उम्मीद है कि आपके यहाँ अच्छा मौसम हो!",
                    "मौसम हमेशा एक अच्छा विषय है! आपके क्षेत्र में मौसम कैसा है?",
                    "मुझे मौसम के बारे में बताना अच्छा लगेगा, लेकिन मेरे पास अभी वह डेटा नहीं है।"
                ]
            },
            "default": {
                "en": [
                    "That's interesting! Tell me more about it.",
                    "I see! What else would you like to discuss?",
                    "Fascinating! Can you elaborate on that?",
                    "I understand. What's on your mind?"
                ],
                "hi": [
                    "यह दिलचस्प है! इसके बारे में और बताएं।",
                    "मैं समझ गया! आप और किस बारे में चर्चा करना चाहेंगे?",
                    "आकर्षक! क्या आप इस पर विस्तार से बता सकते हैं?",
                    "मैं समझ गया। आपके मन में क्या है?"
                ]
            },
            "compliment": {
                "en": [
                    "Thank you so much! You're very kind!",
                    "That's so sweet of you to say!",
                    "I appreciate your kind words!"
                ],
                "hi": [
                    "बहुत धन्यवाद! आप बहुत दयालु हैं!",
                    "यह कहना आपकी बहुत दया है!",
                    "मैं आपके दयालु शब्दों की सराहना करता हूँ!"
                ]
            }
        }
    
    def _load_emotion_keywords(self) -> Dict:
        """Load keywords for emotion detection."""
        return {
            "happy": {
                "en": ["happy", "joy", "excited", "great", "wonderful", "amazing", "fantastic", "good", "excellent"],
                "hi": ["खुश", "खुशी", "अच्छा", "शानदार", "बहुत बढ़िया", "उत्साहित", "प्रसन्न"]
            },
            "sad": {
                "en": ["sad", "sorry", "unhappy", "depressed", "down", "bad", "terrible", "awful", "upset"],
                "hi": ["दुखी", "उदास", "बुरा", "परेशान", "गमगीन", "निराश"]
            },
            "angry": {
                "en": ["angry", "mad", "furious", "annoyed", "frustrated", "irritated"],
                "hi": ["गुस्सा", "क्रोधित", "नाराज", "परेशान", "चिढ़"]
            },
            "neutral": {
                "en": ["okay", "fine", "normal", "regular"],
                "hi": ["ठीक", "सामान्य", "साधारण"]
            }
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of input text.
        
        Args:
            text: Input text
            
        Returns:
            Language code ('en' or 'hi')
        """
        try:
            lang = detect(text)
            # Map detected languages to supported ones
            if lang in ['hi', 'mr', 'ne']:  # Hindi and related languages
                return 'hi'
            else:
                return 'en'
        except:
            return 'en'  # Default to English
    
    def detect_intent(self, text: str, language: str) -> str:
        """
        Detect intent from user message.
        
        Args:
            text: User message
            language: Language code
            
        Returns:
            Intent category
        """
        text_lower = text.lower()
        
        # Define patterns for different intents
        patterns = {
            "greetings": {
                "en": ["hello", "hi", "hey", "good morning", "good evening", "greetings"],
                "hi": ["नमस्ते", "हैलो", "हाय", "नमस्कार", "सुप्रभात", "शुभ संध्या"]
            },
            "how_are_you": {
                "en": ["how are you", "how do you do", "how's it going", "what's up"],
                "hi": ["कैसे हैं", "कैसे हो", "क्या हाल", "कैसा चल रहा"]
            },
            "goodbye": {
                "en": ["bye", "goodbye", "see you", "take care", "farewell"],
                "hi": ["अलविदा", "बाय", "फिर मिलेंगे", "जाता हूँ", "चलता हूँ"]
            },
            "help": {
                "en": ["help", "assist", "support", "what can you do"],
                "hi": ["मदद", "सहायता", "सहारा", "आप क्या कर सकते"]
            },
            "weather": {
                "en": ["weather", "rain", "sunny", "cloudy", "temperature"],
                "hi": ["मौसम", "बारिश", "धूप", "बादल", "तापमान"]
            },
            "compliment": {
                "en": ["good", "nice", "great", "awesome", "you're good", "well done"],
                "hi": ["अच्छा", "बहुत बढ़िया", "शानदार", "वाह", "बहुत अच्छा"]
            }
        }
        
        # Check for pattern matches
        for intent, lang_patterns in patterns.items():
            if language in lang_patterns:
                for pattern in lang_patterns[language]:
                    if pattern in text_lower:
                        return intent
        
        return "default"
    
    def detect_emotion(self, text: str, language: str) -> str:
        """
        Detect emotion from user message.
        
        Args:
            text: User message
            language: Language code
            
        Returns:
            Emotion category
        """
        text_lower = text.lower()
        
        for emotion, lang_keywords in self.emotion_keywords.items():
            if language in lang_keywords:
                for keyword in lang_keywords[language]:
                    if keyword in text_lower:
                        return emotion
        
        return "neutral"
    
    def generate_response(self, user_input: str) -> Tuple[str, str]:
        """
        Generate response to user input.
        
        Args:
            user_input: User's message
            
        Returns:
            Tuple of (response_text, emotion)
        """
        if not user_input.strip():
            return "I didn't catch that. Could you please say something?", "neutral"
        
        # Detect language and intent
        language = self.detect_language(user_input)
        intent = self.detect_intent(user_input, language)
        emotion = self.detect_emotion(user_input, language)
        
        # Store conversation
        self.conversation_history.append({
            "user": user_input,
            "language": language,
            "intent": intent,
            "emotion": emotion
        })
        
        # Generate response based on intent
        if intent in self.responses and language in self.responses[intent]:
            response = random.choice(self.responses[intent][language])
        else:
            response = random.choice(self.responses["default"][language])
        
        # Determine response emotion based on user emotion
        response_emotion = self._map_response_emotion(emotion)
        
        return response, response_emotion
    
    def _map_response_emotion(self, user_emotion: str) -> str:
        """
        Map user emotion to appropriate response emotion.
        
        Args:
            user_emotion: Detected user emotion
            
        Returns:
            Response emotion for avatar
        """
        emotion_mapping = {
            "happy": "happy",
            "sad": "neutral",  # Be supportive but not too sad
            "angry": "neutral",  # Stay calm
            "neutral": "neutral"
        }
        
        return emotion_mapping.get(user_emotion, "neutral")
    
    def get_conversation_context(self) -> List[Dict]:
        """Get recent conversation history."""
        return self.conversation_history[-5:]  # Last 5 exchanges


def test_chatbot():
    """Test function for chatbot."""
    chatbot = MultilingualChatbot()
    
    test_inputs = [
        "Hello!",
        "How are you?",
        "I'm feeling happy today!",
        "नमस्ते!",
        "आप कैसे हैं?",
        "मैं खुश हूँ",
        "Goodbye!"
    ]
    
    print("Testing Multilingual Chatbot:")
    for user_input in test_inputs:
        response, emotion = chatbot.generate_response(user_input)
        lang = chatbot.detect_language(user_input)
        print(f"User ({lang}): {user_input}")
        print(f"Bot: {response} [Emotion: {emotion}]")
        print("-" * 50)


if __name__ == "__main__":
    test_chatbot()