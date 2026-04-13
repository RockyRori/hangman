export type Side = "player" | "agent";

export interface SideState {
  guesses: string[];
  wrongAttempts: number;
  currentLetter: string | null;
  finished: boolean;
  success: boolean;
  steps: number;
}

export interface RoundResult {
  round: number;
  playerWord: string;
  agentWord: string;
  playerSuccess: boolean;
  agentSuccess: boolean;
  winner: "Player" | "AI" | "Draw";
}

export interface ScoreBoard {
  player: number;
  agent: number;
  draws: number;
}

export type QModel = Record<string, number>;
