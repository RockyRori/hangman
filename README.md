# Hangman Reinforcement Learning Game

This project implements a reinforcement learning-based Hangman game using Pygame.

## Installation and Setup

Follow these steps to set up and run the project:

### 1. Clone the Repository
```bash
git clone https://github.com/RockyRori/hangman.git
cd hangman
```

### 2. Install Required Dependencies
Ensure you have Python installed, then install dependencies using:
```bash
pip install -r requirements.txt
```

### 3. Run the Game
Execute the main script to start the game:
```bash
python main.py
```

## 4. Explanation of Key Parameters

These four parameters can be modified in the script to observe different effects:

- `word_list`:  
  This list contains the words used in the Hangman game. Modifying it will change the possible words that the player needs to guess.

- `max_rounds`:  
  This sets the number of rounds in the game. Increasing or decreasing this value will change the total number of games before the session ends.

- `game_frequency_millisecond`:  
  This parameter controls the delay (in milliseconds) between each decision made by the AI. A lower value will make the AI play faster, while a higher value will slow it down.

- `load_model`:  
  If set to `True`, the game will attempt to load a pre-trained Q-learning model (`q_table.pkl`). If set to `False`, it will start training a new model from scratch.

By modifying these parameters, you can see how they affect the game’s difficulty, learning behavior, and responsiveness.

## 5. User Play
If you want to play this game, you can goto my website:

[海星快乐屋](https://rockyrori.github.io/haixing/#/Ghangman)

## 6. Video Presentation
https://www.bilibili.com/video/BV13rPiexEL8/
https://youtu.be/CIxFnksE01M
