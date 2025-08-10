---
title: hangman
app_file: app.py
sdk: gradio
sdk_version: 5.42.0
---

🎯 AI-Powered Hangman Game
An intelligent twist on the classic hangman game that leverages OpenAI's GPT models to dynamically generate words based on difficulty levels.
🤖 How AI is Used

Dynamic Word Generation: OpenAI API generates contextually appropriate words for each difficulty level (easy: 4-6 letters, medium: 6-8 letters, hard: 8-12 letters)
Intelligent Selection: AI ensures words are common, fair, and age-appropriate while avoiding proper nouns, abbreviations, and overly obscure terms
Adaptive Difficulty: Machine learning helps maintain balanced challenge levels across different player skill levels

✨ Features

Interactive web interface built with Gradio
Real-time hangman ASCII art visualization
Three difficulty modes with AI-curated word selection
Input validation and game state management
Fallback system for offline play