import pygame
import random
import pickle

# 初始化 Pygame
# Initialize Pygame
pygame.init()

# 屏幕尺寸
# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 650, 630
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("吊死鬼_强化学习版本")

# 字体
# Font settings
font = pygame.font.SysFont("DengXian", 36)
title_font = pygame.font.SysFont("Comic Sans MS", 48, bold=True, italic=True)
small_font = pygame.font.SysFont("Arial", 20)

# 颜色
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# 彩虹颜色
# Colors
RAINBOW_COLORS = [
    (255, 0, 0),
    (255, 127, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 0, 255),
    (75, 0, 130),
    (148, 0, 211)
]

# 强化学习参数
# Reinforcement learning parameters
Q_table = {}
alpha = 0.1
gamma = 0.9
epsilon = 0.05

# 游戏变量
# Game variables
# 可以修改的参数
# editable variables
word_list = ["brave", "grain", "spire"]
max_rounds = 10
game_frequency_millisecond = 200
load_model = False
q_table_file = "q_table.pkl"
# 固定的参数
# fixed variables
current_round = 1
score = 0
correct_count = 0
wrong_count = 0
current_letter = ""
secret_word = random.choice(word_list)
guesses = set()
wrong_attempts = 0
max_attempts = 7
time_since_last_guess = 0

# 键盘布局
# Keyboard layout
keyboard_rows = [
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm"
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


# 获取当前状态
# Get current state
def get_state(secret_word, guesses):
    observed_word = "".join(letter if letter in guesses else "_" for letter in secret_word)
    return observed_word


# 更新 Q 值
# Update Q value
def update_Q(state, action, reward, next_state):
    current_Q = Q_table.get((state, action), 0)
    next_max_Q = max(Q_table.get((next_state, a), 0) for a in "abcdefghijklmnopqrstuvwxyz" if a not in guesses)
    Q_table[(state, action)] = current_Q + alpha * (reward + gamma * next_max_Q - current_Q)


# 选择动作（字母）
# Choose action (letter)
def choose_action(state, guesses):
    if random.random() < epsilon:
        return random.choice([letter for letter in "abcdefghijklmnopqrstuvwxyz" if letter not in guesses])
    else:
        q_values = {a: Q_table.get((state, a), 0) for a in "abcdefghijklmnopqrstuvwxyz" if a not in guesses}
        return max(q_values, key=q_values.get,
                   default=random.choice([letter for letter in "abcdefghijklmnopqrstuvwxyz" if letter not in guesses]))


# 奖励规则
# Reward rule
def get_reward(correct, finished, success):
    if success:
        return 10
    elif finished and not success:
        return -10
    elif correct:
        return 2
    else:
        return -1


# 绘制游戏画面
# Draw the game screen
def draw_game():
    screen.fill(WHITE)

    # 绘制标题
    title_surface = title_font.render("HANGMAN", True, BLACK)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
    screen.blit(title_surface, title_rect)

    observed_word = "".join(
        letter if letter in guesses else "_" for letter in secret_word
    )
    word_surface = font.render("单词: " + " ".join(observed_word), True, BLACK)
    screen.blit(word_surface, (50, 100))

    remaining_attempts_surface = font.render(
        f"剩余尝试: {max_attempts - wrong_attempts}", True, RED
    )
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
    if wrong_attempts >= 1:
        pygame.draw.circle(screen, RAINBOW_COLORS[0], (hangman_x + 50, hangman_y + 20), 20)
    if wrong_attempts >= 2:
        pygame.draw.line(screen, RAINBOW_COLORS[1], (hangman_x + 50, hangman_y + 40), (hangman_x + 50, hangman_y + 100),
                         5)
    if wrong_attempts >= 3:
        pygame.draw.line(screen, RAINBOW_COLORS[2], (hangman_x + 50, hangman_y + 60), (hangman_x + 20, hangman_y + 80),
                         5)
    if wrong_attempts >= 4:
        pygame.draw.line(screen, RAINBOW_COLORS[3], (hangman_x + 50, hangman_y + 60), (hangman_x + 80, hangman_y + 80),
                         5)
    if wrong_attempts >= 5:
        pygame.draw.line(screen, RAINBOW_COLORS[4], (hangman_x + 50, hangman_y + 100),
                         (hangman_x + 20, hangman_y + 140), 5)
    if wrong_attempts >= 6:
        pygame.draw.line(screen, RAINBOW_COLORS[5], (hangman_x + 50, hangman_y + 100),
                         (hangman_x + 80, hangman_y + 140), 5)
    if wrong_attempts >= 7:
        pygame.draw.line(screen, RAINBOW_COLORS[6], (hangman_x + 50, hangman_y + 100),
                         (hangman_x + 80, hangman_y + 180), 5)

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


if __name__ == '__main__':
    if load_model:
        try:
            with open(q_table_file, "rb") as f:
                Q_table = pickle.load(f)
                print("Q表加载成功！")
        except FileNotFoundError:
            print("未找到Q表文件，使用新表。")
            Q_table = {}
    else:
        Q_table = {}

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
            if letter not in guesses:
                guesses.add(letter)
                correct = letter in secret_word
                if correct:
                    score += 2
                else:
                    wrong_attempts += 1
                    score -= 1

            next_state = get_state(secret_word, guesses)
            finished = wrong_attempts >= max_attempts or "_" not in "".join(
                letter if letter in guesses else "_" for letter in secret_word
            )
            success = "_" not in "".join(
                letter if letter in guesses else "_" for letter in secret_word
            )

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
                    secret_word = random.choice(word_list)
                    guesses.clear()
                    wrong_attempts = 0
                    current_letter = ""
        draw_game()
        clock.tick(60)
    pygame.quit()
    if load_model:
        with open(q_table_file, "wb") as f:
            pickle.dump(Q_table, f)
            print("Q表已保存！")
