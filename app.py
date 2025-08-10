import gradio as gr
import openai
import random
import re
from dotenv import load_dotenv

load_dotenv(override=True)

class HangmanGame:
    def __init__(self):
        self.word = ""
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.max_wrong_guesses = 6
        self.game_over = False
        self.won = False
        
    def get_word_from_ai(self, difficulty="medium"):
        """Get a word from OpenAI based on difficulty"""
        system_prompt = """You are a hangman game assistant. Your job is to provide a single word for the hangman game.

            Rules:
            1. Return ONLY the word, nothing else
            2. Word must be a common English word
            3. No proper nouns, abbreviations, or hyphenated words
            4. Word length based on difficulty:
            - Easy: 4-6 letters
            - Medium: 6-8 letters  
            - Hard: 8-12 letters
            5. Choose words that are challenging but fair
            6. Avoid overly obscure words

            Return only the word in lowercase.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Give me a {difficulty} difficulty word for hangman."}
                ],
                max_tokens=10,
                temperature=0.8
            )

            word = response.choices[0].message.content.strip().lower()
            
            # Clean the word to ensure it's just letters
            word = re.sub(r'[^a-z]', '', word)
            
            return word if word else "python"  # fallback word
        except Exception as e:
            # Fallback words if API fails
            fallback_words = {
                "easy": ["cat", "dog", "house", "tree", "book", "happy"],
                "medium": ["python", "computer", "elephant", "rainbow", "butterfly"],
                "hard": ["programming", "algorithm", "mysterious", "extraordinary"]
            }
            return random.choice(fallback_words.get(difficulty, fallback_words["medium"]))
    
    def start_new_game(self, difficulty):
        """Start a new hangman game"""
        self.word = self.get_word_from_ai(difficulty)
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.game_over = False
        self.won = False
        return self.get_display_word(), self.get_hangman_drawing(), f"New {difficulty} game started! Word has {len(self.word)} letters.", ""
    
    def get_display_word(self):
        """Get the word with guessed letters revealed"""
        display = ""
        for letter in self.word:
            if letter in self.guessed_letters:
                display += letter + " "
            else:
                display += "_ "
        return display.strip()
    
    def get_hangman_drawing(self):
        """Get ASCII art for hangman based on wrong guesses"""
        stages = [
            # Stage 0: Empty gallows
            """
   +---+
   |   |
       |
       |
       |
       |
=========
            """,
            # Stage 1: Head
            """
   +---+
   |   |
   O   |
       |
       |
       |
=========
            """,
            # Stage 2: Body
            """
   +---+
   |   |
   O   |
   |   |
       |
       |
=========
            """,
            # Stage 3: Left arm
            """
   +---+
   |   |
   O   |
  /|   |
       |
       |
=========
            """,
            # Stage 4: Right arm
            """
   +---+
   |   |
   O   |
  /|\\  |
       |
       |
=========
            """,
            # Stage 5: Left leg
            """
   +---+
   |   |
   O   |
  /|\\  |
  /    |
       |
=========
            """,
            # Stage 6: Right leg (game over)
            """
   +---+
   |   |
   O   |
  /|\\  |
  / \\  |
       |
=========
            """
        ]
        return stages[min(self.wrong_guesses, 6)]
    
    def make_guess(self, letter):
        """Process a letter guess"""
        if self.game_over:
            return self.get_display_word(), self.get_hangman_drawing(), "Game is over! Start a new game.", ""
        
        letter = letter.lower().strip()
        
        # Validate input
        if not letter or len(letter) != 1 or not letter.isalpha():
            return self.get_display_word(), self.get_hangman_drawing(), "Please enter a single letter.", ""
        
        if letter in self.guessed_letters:
            return self.get_display_word(), self.get_hangman_drawing(), f"You already guessed '{letter}'. Try a different letter.", ""
        
        # Process the guess
        self.guessed_letters.add(letter)
        
        if letter in self.word:
            # Correct guess
            if set(self.word).issubset(self.guessed_letters):
                # Won the game
                self.game_over = True
                self.won = True
                message = f"🎉 Congratulations! You guessed the word '{self.word}'!"
            else:
                message = f"Good guess! '{letter}' is in the word."
        else:
            # Wrong guess
            self.wrong_guesses += 1
            if self.wrong_guesses >= self.max_wrong_guesses:
                # Lost the game
                self.game_over = True
                message = f"😞 Game Over! The word was '{self.word}'. Try again!"
            else:
                remaining = self.max_wrong_guesses - self.wrong_guesses
                message = f"Sorry, '{letter}' is not in the word. {remaining} guesses remaining."
        
        guessed_list = "Guessed letters: " + ", ".join(sorted(self.guessed_letters))
        
        return self.get_display_word(), self.get_hangman_drawing(), message, guessed_list

# Initialize game
game = HangmanGame()

# Create Gradio interface
with gr.Blocks(title="🎯 AI Hangman Game", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎯 AI Hangman Game")
    gr.Markdown("*An intelligent hangman game powered by OpenAI that generates words based on difficulty level.*")
    
    with gr.Row():
        with gr.Column(scale=1):
            difficulty = gr.Radio(
                choices=["easy", "medium", "hard"], 
                value="medium", 
                label="Difficulty Level"
            )
            new_game_btn = gr.Button("🎮 Start New Game", variant="primary")
            
            letter_input = gr.Textbox(
                label="Enter your guess (single letter):",
                placeholder="Type a letter...",
                max_lines=1
            )
            guess_btn = gr.Button("🎯 Make Guess", variant="secondary")
            
        with gr.Column(scale=2):
            word_display = gr.Textbox(
                label="Word:",
                value="Click 'Start New Game' to begin!",
                interactive=False,
                text_align="center"
            )
            
            hangman_display = gr.Code(
                label="Hangman:",
                value="Ready to play!",
                language=None,
                interactive=False
            )
    
    message_display = gr.Textbox(
        label="Message:",
        interactive=False
    )
    
    guessed_letters_display = gr.Textbox(
        label="Progress:",
        interactive=False
    )
    
    # Event handlers
    new_game_btn.click(
        fn=game.start_new_game,
        inputs=[difficulty],
        outputs=[word_display, hangman_display, message_display, guessed_letters_display]
    )
    
    guess_btn.click(
        fn=game.make_guess,
        inputs=[letter_input],
        outputs=[word_display, hangman_display, message_display, guessed_letters_display]
    )
    
    letter_input.submit(
        fn=game.make_guess,
        inputs=[letter_input],
        outputs=[word_display, hangman_display, message_display, guessed_letters_display]
    )

if __name__ == "__main__":
    demo.launch(share=True)