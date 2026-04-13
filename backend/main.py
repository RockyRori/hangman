import json
import pickle
import random
from pathlib import Path

import pygame


pygame.init()

ROOT_DIR = Path(__file__).resolve().parents[1]
WORD_BANK_FILE = ROOT_DIR / "shared" / "words.json"
Q_TABLE_FILE = Path(__file__).resolve().with_name("q_table.pkl")

SCREEN_WIDTH, SCREEN_HEIGHT = 650, 630
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("吊死鬼-强化学习版本")

font = pygame.font.SysFont("DengXian", 36)
title_font = pygame.font.SysFont("Comic Sans MS", 48, bold=True, italic=True)
small_font = pygame.font.SysFont("Arial", 20)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

RAINBOW_COLORS = [
    (255, 0, 0),
    (255, 127, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 0, 255),
    (75, 0, 130),
    (148, 0, 211),
]

Q_table = {}
alpha = 0.1
gamma = 0.9
epsilon = 0.05

max_rounds = 10
training_word_count = 100
game_frequency_millisecond = 200
load_model = True
save_model = True
max_attempts = 13
hangman_stages = 7

current_round = 1
score = 0
correct_count = 0
wrong_count = 0
current_letter = ""
guesses = set()
wrong_attempts = 0
time_since_last_guess = 0

keyboard_rows = [
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
]
key_positions = {}
key_width, key_height = 30, 40
key_spacing = 10
keyboard_top = SCREEN_HEIGHT - 150

x_start = 50
for row_index, row in enumerate(keyboard_rows):
    y = keyboard_top + row_index * (key_height + key_spacing)
    x = x_start + row_index * (key_width // 2)
    for letter in row:
        key_positions[letter] = (x, y)
        x += key_width + key_spacing


def load_word_bank() -> list[str]:
    with WORD_BANK_FILE.open("r", encoding="utf-8") as handle:
        words = json.load(handle)

    normalized = [word.strip().lower() for word in words if word and word.strip()]
    unique_words = list(dict.fromkeys(normalized))
    if not unique_words:
        raise ValueError("共享词库为空。")

    return unique_words


def sample_training_words(word_bank: list[str], sample_size: int) -> list[str]:
    if len(word_bank) <= sample_size:
        return word_bank.copy()

    return random.sample(word_bank, sample_size)


def get_state(secret_word: str, selected_guesses: set[str]) -> str:
    return "".join(letter if letter in selected_guesses else "_" for letter in secret_word)


def update_Q(state: str, action: str, reward: int, next_state: str) -> None:
    current_Q = Q_table.get((state, action), 0)
    available_actions = [letter for letter in "abcdefghijklmnopqrstuvwxyz" if letter not in guesses]
    next_max_Q = max((Q_table.get((next_state, letter), 0) for letter in available_actions), default=0)
    Q_table[(state, action)] = current_Q + alpha * (reward + gamma * next_max_Q - current_Q)


def choose_action(state: str, selected_guesses: set[str]) -> str:
    available_letters = [letter for letter in "abcdefghijklmnopqrstuvwxyz" if letter not in selected_guesses]
    if not available_letters:
        return "a"

    if random.random() < epsilon:
        return random.choice(available_letters)

    q_values = {letter: Q_table.get((state, letter), 0) for letter in available_letters}
    return max(q_values, key=q_values.get)


def get_reward(correct: bool, finished: bool, success: bool) -> int:
    if success:
        return 10
    if finished:
        return -10
    if correct:
        return 2
    return -1


def draw_game(secret_word: str) -> None:
    screen.fill(WHITE)

    title_surface = title_font.render("HANGMAN", True, BLACK)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
    screen.blit(title_surface, title_rect)

    observed_word = get_state(secret_word, guesses)
    word_surface = font.render("单词: " + " ".join(observed_word), True, BLACK)
    screen.blit(word_surface, (50, 100))

    remaining_attempts_surface = font.render(f"剩余尝试: {max_attempts - wrong_attempts}", True, RED)
    screen.blit(remaining_attempts_surface, (50, 150))

    current_letter_surface = font.render(f"当前字母: {current_letter}", True, BLACK)
    screen.blit(current_letter_surface, (50, 200))

    score_surface = font.render(f"奖励分数: {score}", True, BLACK)
    screen.blit(score_surface, (50, 250))

    round_surface = font.render(f"当前轮次: {current_round}/{max_rounds}", True, BLACK)
    screen.blit(round_surface, (50, 300))

    correct_surface = font.render(f"猜对单词: {correct_count}", True, BLACK)
    screen.blit(correct_surface, (50, 350))

    wrong_surface = font.render(f"答错单词: {wrong_count}", True, BLACK)
    screen.blit(wrong_surface, (50, 400))

    hangman_x = 360
    hangman_y = 125
    stage = 0 if wrong_attempts <= 0 else min(
        hangman_stages,
        ((wrong_attempts * hangman_stages) + max_attempts - 1) // max_attempts,
    )

    if stage >= 1:
        pygame.draw.circle(screen, RAINBOW_COLORS[0], (hangman_x + 50, hangman_y + 20), 20)
    if stage >= 2:
        pygame.draw.line(screen, RAINBOW_COLORS[1], (hangman_x + 50, hangman_y + 40), (hangman_x + 50, hangman_y + 100), 5)
    if stage >= 3:
        pygame.draw.line(screen, RAINBOW_COLORS[2], (hangman_x + 50, hangman_y + 60), (hangman_x + 20, hangman_y + 80), 5)
    if stage >= 4:
        pygame.draw.line(screen, RAINBOW_COLORS[3], (hangman_x + 50, hangman_y + 60), (hangman_x + 80, hangman_y + 80), 5)
    if stage >= 5:
        pygame.draw.line(screen, RAINBOW_COLORS[4], (hangman_x + 50, hangman_y + 100), (hangman_x + 20, hangman_y + 140), 5)
    if stage >= 6:
        pygame.draw.line(screen, RAINBOW_COLORS[5], (hangman_x + 50, hangman_y + 100), (hangman_x + 80, hangman_y + 140), 5)
    if stage >= 7:
        pygame.draw.line(screen, RAINBOW_COLORS[6], (hangman_x + 50, hangman_y + 100), (hangman_x + 80, hangman_y + 180), 5)

    for letter, (x, y) in key_positions.items():
        rect = pygame.Rect(x, y, key_width, key_height)
        pygame.draw.rect(screen, GRAY, rect)
        if letter in guesses:
            pygame.draw.line(screen, RED, (x, y), (x + key_width, y + key_height), 2)
            pygame.draw.line(screen, RED, (x + key_width, y), (x, y + key_height), 2)
        text_surface = small_font.render(letter, True, BLACK)
        text_rect = text_surface.get_rect(center=(x + key_width // 2, y + key_height // 2))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()


if __name__ == "__main__":
    word_bank = load_word_bank()
    training_words = sample_training_words(word_bank, training_word_count)
    secret_word = random.choice(training_words)

    print(f"已从 {WORD_BANK_FILE} 加载 {len(word_bank)} 个共享单词。")
    print(f"本轮训练将从词库中随机抽取 {len(training_words)} 个单词。")

    if load_model and Q_TABLE_FILE.exists():
        with Q_TABLE_FILE.open("rb") as handle:
            Q_table = pickle.load(handle)
        print("Q 表加载成功。")
    else:
        Q_table = {}
        print("未找到可用 Q 表，将从空白 Q 表开始训练。")

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        time_since_last_guess += clock.get_time()
        if time_since_last_guess >= game_frequency_millisecond:
            state = get_state(secret_word, guesses)
            letter = choose_action(state, guesses)
            current_letter = letter

            correct = letter in secret_word
            if letter not in guesses:
                guesses.add(letter)
                if correct:
                    score += 2
                else:
                    wrong_attempts += 1
                    score -= 1

            next_state = get_state(secret_word, guesses)
            success = "_" not in next_state
            finished = success or wrong_attempts >= max_attempts

            reward = get_reward(correct, finished, success)
            update_Q(state, letter, reward, next_state)
            time_since_last_guess = 0

            if finished:
                if success:
                    correct_count += 1
                    score += 5
                else:
                    wrong_count += 1

                current_round += 1
                if current_round > max_rounds:
                    running = False
                else:
                    secret_word = random.choice(training_words)
                    guesses.clear()
                    wrong_attempts = 0
                    current_letter = ""

        draw_game(secret_word)
        clock.tick(60)

    pygame.quit()

    if save_model:
        with Q_TABLE_FILE.open("wb") as handle:
            pickle.dump(Q_table, handle)
        print(f"Q 表已保存到 {Q_TABLE_FILE}。")
