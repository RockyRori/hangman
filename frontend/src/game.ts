import type { QModel, RoundResult, ScoreBoard, SideState } from "./types";

export const MAX_ATTEMPTS = 9;
export const ALPHABET = "abcdefghijklmnopqrstuvwxyz".split("");

export const createInitialSideState = (): SideState => ({
  guesses: [],
  wrongAttempts: 0,
  currentLetter: null,
  finished: false,
  success: false,
  steps: 0
});

export const getObservedWord = (word: string, guesses: string[]): string =>
  word
    .split("")
    .map((letter) => (guesses.includes(letter) ? letter : "_"))
    .join("");

export const isSuccess = (word: string, guesses: string[]): boolean => !getObservedWord(word, guesses).includes("_");

export const keyFor = (state: string, action: string): string => `${state}|${action}`;

const chooseUnusedLetters = (guesses: string[]) => ALPHABET.filter((letter) => !guesses.includes(letter));

export const chooseAgentLetter = (word: string, guesses: string[], qModel: QModel): string => {
  const observed = getObservedWord(word, guesses);
  const candidates = chooseUnusedLetters(guesses);

  const ranked = candidates
    .map((letter) => ({
      letter,
      value: qModel[keyFor(observed, letter)] ?? 0,
      reveals: word.includes(letter) ? 1 : 0
    }))
    .sort((left, right) => {
      if (right.value !== left.value) {
        return right.value - left.value;
      }

      if (right.reveals !== left.reveals) {
        return right.reveals - left.reveals;
      }

      return left.letter.localeCompare(right.letter);
    });

  return ranked[0]?.letter ?? candidates[0] ?? "a";
};

export const applyGuess = (word: string, state: SideState, letter: string): SideState => {
  if (state.finished || state.guesses.includes(letter)) {
    return state;
  }

  const guesses = [...state.guesses, letter];
  const wrongAttempts = word.includes(letter) ? state.wrongAttempts : state.wrongAttempts + 1;
  const success = isSuccess(word, guesses);
  const finished = success || wrongAttempts >= MAX_ATTEMPTS;

  return {
    guesses,
    wrongAttempts,
    currentLetter: letter,
    finished,
    success,
    steps: state.steps + 1
  };
};

export const settleRound = (
  round: number,
  playerWord: string,
  agentWord: string,
  playerState: SideState,
  agentState: SideState
): RoundResult => {
  const playerWon =
    Number(playerState.success) > Number(agentState.success) ||
    (playerState.success === agentState.success && playerState.wrongAttempts < agentState.wrongAttempts) ||
    (playerState.success === agentState.success &&
      playerState.wrongAttempts === agentState.wrongAttempts &&
      playerState.steps < agentState.steps);

  const agentWon =
    Number(agentState.success) > Number(playerState.success) ||
    (playerState.success === agentState.success && agentState.wrongAttempts < playerState.wrongAttempts) ||
    (playerState.success === agentState.success &&
      agentState.wrongAttempts === playerState.wrongAttempts &&
      agentState.steps < playerState.steps);

  return {
    round,
    playerWord,
    agentWord,
    playerSuccess: playerState.success,
    agentSuccess: agentState.success,
    winner: playerWon ? "Player" : agentWon ? "AI" : "Draw"
  };
};

export const updateScore = (score: ScoreBoard, result: RoundResult): ScoreBoard => {
  if (result.winner === "Player") {
    return { ...score, player: score.player + 1 };
  }

  if (result.winner === "AI") {
    return { ...score, agent: score.agent + 1 };
  }

  return { ...score, draws: score.draws + 1 };
};

export const pickRoundWords = (wordBank: string[]): { playerWord: string; agentWord: string } => {
  if (wordBank.length === 0) {
    return { playerWord: "", agentWord: "" };
  }

  if (wordBank.length === 1) {
    return { playerWord: wordBank[0], agentWord: wordBank[0] };
  }

  const playerIndex = Math.floor(Math.random() * wordBank.length);
  let agentIndex = Math.floor(Math.random() * wordBank.length);

  while (agentIndex === playerIndex) {
    agentIndex = Math.floor(Math.random() * wordBank.length);
  }

  return {
    playerWord: wordBank[playerIndex],
    agentWord: wordBank[agentIndex]
  };
};
