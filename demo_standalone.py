#!/usr/bin/env python3
"""
Standalone demo script for the 3D Talking Avatar system.
This script demonstrates the core functionality without requiring all dependencies.
"""

import json
import os

def demo_text_to_visemes():
    """Demonstrate text to viseme conversion."""
    print("🗣️ 3D Talking Avatar - Standalone Demo")
    print("=" * 50)
    
    # Demo input
    demo_text = "Hello world!"
    print(f"Input Text: '{demo_text}'")
    print()
    
    # Simulate phoneme extraction
    demo_phonemes = [
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
    
    print("Extracted Phonemes:")
    for i, phoneme in enumerate(demo_phonemes):
        print(f"  {i+1}. {phoneme['phoneme']} ({phoneme['start_time']:.1f}s - {phoneme['end_time']:.1f}s)")
    print()
    
    # Phoneme to viseme mapping
    phoneme_to_viseme = {
        'h': 'A', 'ə': 'A', 'l': 'L', 'oʊ': 'O', 'sil': 'X',
        'w': 'W', 'ɜ': 'A', 'd': 'T'
    }
    
    # Viseme descriptions
    viseme_descriptions = {
        'A': {'name': 'open', 'mouth_open': 0.8, 'mouth_width': 0.6, 'lip_pucker': 0.0},
        'L': {'name': 'lateral', 'mouth_open': 0.3, 'mouth_width': 0.6, 'lip_pucker': 0.0},
        'O': {'name': 'back', 'mouth_open': 0.5, 'mouth_width': 0.4, 'lip_pucker': 0.3},
        'X': {'name': 'silence', 'mouth_open': 0.0, 'mouth_width': 0.5, 'lip_pucker': 0.0},
        'W': {'name': 'approximant', 'mouth_open': 0.2, 'mouth_width': 0.3, 'lip_pucker': 0.5},
        'T': {'name': 'tongue_tip', 'mouth_open': 0.2, 'mouth_width': 0.6, 'lip_pucker': 0.0}
    }
    
    # Convert to visemes
    viseme_timeline = []
    for phoneme_info in demo_phonemes:
        phoneme = phoneme_info['phoneme']
        viseme = phoneme_to_viseme.get(phoneme, 'X')
        params = viseme_descriptions[viseme]
        
        viseme_entry = {
            'time': phoneme_info['start_time'],
            'viseme': viseme,
            'duration': phoneme_info['end_time'] - phoneme_info['start_time'],
            'parameters': {
                'mouth_open': params['mouth_open'],
                'mouth_width': params['mouth_width'],
                'lip_pucker': params['lip_pucker']
            },
            'description': f"{params['name']} viseme",
            'original_phoneme': phoneme
        }
        viseme_timeline.append(viseme_entry)
    
    print("Generated Viseme Timeline:")
    for i, viseme in enumerate(viseme_timeline):
        print(f"  {i+1}. {viseme['viseme']} at {viseme['time']:.1f}s - {viseme['description']}")
        print(f"     Parameters: open={viseme['parameters']['mouth_open']:.1f}, "
              f"width={viseme['parameters']['mouth_width']:.1f}, "
              f"pucker={viseme['parameters']['lip_pucker']:.1f}")
    print()
    
    # Create Three.js compatible animation data
    animation_data = {
        'name': 'lip_sync_animation',
        'duration': viseme_timeline[-1]['time'] + viseme_timeline[-1]['duration'],
        'tracks': []
    }
    
    # Create tracks for each parameter
    for param in ['mouth_open', 'mouth_width', 'lip_pucker']:
        track = {
            'name': f'facial.{param}',
            'type': 'number',
            'times': [v['time'] for v in viseme_timeline],
            'values': [v['parameters'][param] for v in viseme_timeline]
        }
        animation_data['tracks'].append(track)
    
    print("Three.js Animation Data:")
    print(json.dumps(animation_data, indent=2))
    print()
    
    # Save to file
    with open('demo_viseme_output.json', 'w') as f:
        json.dump({
            'input_text': demo_text,
            'phoneme_timeline': demo_phonemes,
            'viseme_timeline': viseme_timeline,
            'animation_data': animation_data
        }, f, indent=2)
    
    print("✅ Demo complete! Output saved to 'demo_viseme_output.json'")
    print()
    print("Integration Code Examples:")
    print("-" * 30)
    
    print("JavaScript (Three.js):")
    print("""
// Apply viseme to 3D avatar
function applyViseme(avatar, viseme) {
    const params = viseme.parameters;
    avatar.morphTargetInfluences[0] = params.mouth_open;
    avatar.morphTargetInfluences[1] = params.mouth_width;
    avatar.morphTargetInfluences[2] = params.lip_pucker;
}

// Animate timeline
visemeTimeline.forEach((viseme, index) => {
    setTimeout(() => {
        applyViseme(avatar, viseme);
    }, viseme.time * 1000);
});
""")
    
    print("Unity C#:")
    print("""
// Apply viseme to SkinnedMeshRenderer
public void ApplyViseme(VisemeData viseme) {
    var renderer = GetComponent<SkinnedMeshRenderer>();
    renderer.SetBlendShapeWeight(0, viseme.mouth_open * 100);
    renderer.SetBlendShapeWeight(1, viseme.mouth_width * 100);
    renderer.SetBlendShapeWeight(2, viseme.lip_pucker * 100);
}
""")

def demo_chatbot():
    """Demonstrate chatbot functionality."""
    print("\n🤖 Chatbot Demo")
    print("=" * 20)
    
    # Sample responses
    responses = {
        "hello": ("Hello! How can I help you today?", "happy"),
        "how are you": ("I'm doing great, thank you for asking!", "happy"),
        "sad": ("I understand. Is there anything I can do to help?", "neutral"),
        "goodbye": ("Goodbye! It was nice talking to you!", "happy")
    }
    
    test_inputs = ["hello", "how are you", "I'm feeling sad", "goodbye"]
    
    for user_input in test_inputs:
        # Simple intent matching
        for key, (response, emotion) in responses.items():
            if key in user_input.lower():
                print(f"User: {user_input}")
                print(f"Bot: {response} [Emotion: {emotion}]")
                print()
                break
        else:
            print(f"User: {user_input}")
            print(f"Bot: That's interesting! Tell me more. [Emotion: neutral]")
            print()

def main():
    """Run the complete demo."""
    print("🚀 Starting 3D Talking Avatar Demo...")
    print()
    
    # Demo components
    demo_text_to_visemes()
    demo_chatbot()
    
    print("📋 Next Steps:")
    print("1. Install dependencies: pip install -r requirements_avatar.txt")
    print("2. Download Vosk models (see README.md)")
    print("3. Run the full server: python3 server.py")
    print("4. Open browser: http://localhost:8000")
    print()
    print("Happy hacking! 🎉")

if __name__ == "__main__":
    main()