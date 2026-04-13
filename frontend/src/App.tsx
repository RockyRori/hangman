import { useEffect, useRef, useState } from "react";
import {
  ALPHABET,
  MAX_ATTEMPTS,
  applyGuess,
  chooseAgentLetter,
  createInitialSideState,
  getObservedWord,
  pickRoundWords,
  settleRound,
  updateScore
} from "./game";
import { SoundBoard } from "./sound";
import type { QModel, RoundResult, ScoreBoard, Side, SideState } from "./types";

const TOTAL_ROUNDS = 6;
const HANGMAN_STAGES = 7;

const baseScore: ScoreBoard = {
  player: 0,
  agent: 0,
  draws: 0
};

function App() {
  const soundBoardRef = useRef(new SoundBoard());
  const [qModel, setQModel] = useState<QModel>({});
  const [wordBank, setWordBank] = useState<string[]>([]);
  const [modelReady, setModelReady] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [round, setRound] = useState(1);
  const [playerWord, setPlayerWord] = useState("");
  const [agentWord, setAgentWord] = useState("");
  const [playerState, setPlayerState] = useState<SideState>(createInitialSideState);
  const [agentState, setAgentState] = useState<SideState>(createInitialSideState);
  const [score, setScore] = useState<ScoreBoard>(baseScore);
  const [history, setHistory] = useState<RoundResult[]>([]);

  useEffect(() => {
    Promise.all([
      fetch(`${import.meta.env.BASE_URL}q-table.json`),
      fetch(`${import.meta.env.BASE_URL}words.json`)
    ])
      .then(async ([qTableResponse, wordsResponse]) => {
        if (!qTableResponse.ok) {
          throw new Error(`Model load failed: ${qTableResponse.status}`);
        }

        if (!wordsResponse.ok) {
          throw new Error(`Word bank load failed: ${wordsResponse.status}`);
        }

        const [qTableJson, wordsJson] = await Promise.all([
          qTableResponse.json() as Promise<QModel>,
          wordsResponse.json() as Promise<string[]>
        ]);

        return { qTableJson, wordsJson };
      })
      .then(({ qTableJson, wordsJson }) => {
        const normalizedWords = wordsJson.map((word) => word.toLowerCase()).filter(Boolean);
        const openingWords = pickRoundWords(normalizedWords);

        setQModel(qTableJson);
        setWordBank(normalizedWords);
        setPlayerWord(openingWords.playerWord);
        setAgentWord(openingWords.agentWord);
        setModelReady(true);
      })
      .catch((error: Error) => {
        setLoadError(error.message);
        setModelReady(true);
      });
  }, []);

  const resetMatch = () => {
    const firstWords = pickRoundWords(wordBank);
    setRound(1);
    setPlayerWord(firstWords.playerWord);
    setAgentWord(firstWords.agentWord);
    setPlayerState(createInitialSideState());
    setAgentState(createInitialSideState());
    setScore(baseScore);
    setHistory([]);
  };

  const moveNextRound = (
    nextRound: number,
    nextScore: ScoreBoard,
    nextHistory: RoundResult[],
    finalPlayerState: SideState,
    finalAgentState: SideState
  ) => {
    setScore(nextScore);
    setHistory(nextHistory);
    setRound(nextRound);

    if (nextRound > TOTAL_ROUNDS) {
      setPlayerState(finalPlayerState);
      setAgentState(finalAgentState);
      return;
    }

    const upcomingWords = pickRoundWords(wordBank);
    setPlayerWord(upcomingWords.playerWord);
    setAgentWord(upcomingWords.agentWord);
    setPlayerState(createInitialSideState());
    setAgentState(createInitialSideState());
  };

  const finishIfNeeded = (nextPlayerState: SideState, nextAgentState: SideState) => {
    if (!nextPlayerState.finished && !nextAgentState.finished) {
      setPlayerState(nextPlayerState);
      setAgentState(nextAgentState);
      return;
    }

    const result = settleRound(round, playerWord, agentWord, nextPlayerState, nextAgentState);
    soundBoardRef.current.play(result.winner === "AI" ? "failure" : "success");
    const nextScore = updateScore(score, result);
    const nextHistory = [...history, result];
    const nextRound = round + 1;

    moveNextRound(nextRound, nextScore, nextHistory, nextPlayerState, nextAgentState);
  };

  const matchFinished = round > TOTAL_ROUNDS;

  const handleGuess = (letter: string) => {
    if (!modelReady || round > TOTAL_ROUNDS || playerState.finished || playerState.guesses.includes(letter)) {
      return;
    }

    soundBoardRef.current.play("guess");
    const nextPlayerState = applyGuess(playerWord, playerState, letter);
    let nextAgentState = agentState;

    if (!agentState.finished) {
      const agentLetter = chooseAgentLetter(agentWord, agentState.guesses, qModel);
      nextAgentState = applyGuess(agentWord, agentState, agentLetter);
    }

    finishIfNeeded(nextPlayerState, nextAgentState);
  };

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const letter = event.key.toLowerCase();
      if (!ALPHABET.includes(letter)) {
        return;
      }

      const target = event.target as HTMLElement | null;
      const editable =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target?.isContentEditable;

      if (editable) {
        return;
      }

      event.preventDefault();
      handleGuess(letter);
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [agentState, loadError, matchFinished, modelReady, playerState, playerWord, agentWord, qModel, round, score, history]);

  const renderKeyboard = (side: Side, sideState: SideState) => (
    <div className="keyboard">
      {ALPHABET.map((letter) => {
        const guessed = sideState.guesses.includes(letter);
        const disabled =
          side === "agent" || guessed || !modelReady || loadError !== null || matchFinished || playerState.finished;

        return (
          <button
            key={`${side}-${letter}`}
            type="button"
            className={`key ${guessed ? "guessed" : ""}`}
            disabled={disabled}
            onClick={() => handleGuess(letter)}
          >
            {letter}
          </button>
        );
      })}
    </div>
  );

  const renderHangman = (wrongAttempts: number) => {
    const stage = wrongAttempts <= 0 ? 0 : Math.min(HANGMAN_STAGES, Math.ceil((wrongAttempts / MAX_ATTEMPTS) * HANGMAN_STAGES));

    return (
      <div className="hangman">
        <div className="beam" />
        <div className="rope" />
        {stage >= 1 && <div className="head" />}
        {stage >= 2 && <div className="body" />}
        {stage >= 3 && <div className="arm left" />}
        {stage >= 4 && <div className="arm right" />}
        {stage >= 5 && <div className="leg left" />}
        {stage >= 6 && <div className="leg right" />}
        {stage >= 7 && <div className="spark" />}
      </div>
    );
  };

  const renderPanel = (title: string, side: Side, sideState: SideState, accent: string) => (
    <section className="panel" data-side={side}>
      <div className="panel-header">
        <p className="eyebrow">{side === "player" ? "Human Click" : "Q-Table Policy"}</p>
        <h2>{title}</h2>
        <span className="accent-tag" style={{ backgroundColor: accent }}>
          {side === "player" ? "Manual Guess" : "Auto Guess"}
        </span>
      </div>

      <div className="word-card">
        <span>Observed Word</span>
        <strong>{getObservedWord(side === "player" ? playerWord : agentWord, sideState.guesses).split("").join(" ")}</strong>
      </div>

      <div className="stats">
        <div>
          <span>Attempts Left</span>
          <strong>{MAX_ATTEMPTS - sideState.wrongAttempts}</strong>
        </div>
        <div>
          <span>Latest Letter</span>
          <strong>{sideState.currentLetter ?? "-"}</strong>
        </div>
        <div>
          <span>Status</span>
          <strong>{sideState.success ? "Solved" : sideState.finished ? "Lost" : "Playing"}</strong>
        </div>
      </div>

      {renderHangman(sideState.wrongAttempts)}
      {renderKeyboard(side, sideState)}
    </section>
  );

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <p className="badge">Hangman Arena</p>
          <h1>Player vs Q-Table Agent</h1>
          <p className="subtitle">
            Each side now gets a different answer word. You make a move on the left, the agent answers on the right
            with its own Q-table policy, and the round compares who solves their puzzle more cleanly.
          </p>
        </div>

        <div className="scoreboard">
          <div>
            <span>Player</span>
            <strong>{score.player}</strong>
          </div>
          <div>
            <span>AI</span>
            <strong>{score.agent}</strong>
          </div>
          <div>
            <span>Draws</span>
            <strong>{score.draws}</strong>
          </div>
          <div>
            <span>Round</span>
            <strong>
              {Math.min(round, TOTAL_ROUNDS)} / {TOTAL_ROUNDS}
            </strong>
          </div>
        </div>
      </section>

      <section className="notice-row">
        <div className="notice">
          <strong>Model Source</strong>
          <span>The browser reads `q-table.json`, generated from `backend/q_table.pkl` without changing backend code.</span>
        </div>
        <div className="notice">
          <strong>Round Setup</strong>
          <span>
            {matchFinished
              ? "Match finished. Reset to start again."
              : `Shared bank loaded with ${wordBank.length} words. Player and AI get different random words each round.`}
          </span>
        </div>
        <div className="notice">
          <strong>Input & Sound</strong>
          <span>{loadError ? loadError : modelReady ? "Click or press A-Z. Guess plays a click tone; rounds end with win or fail audio." : "Loading model..."}</span>
        </div>
      </section>

      <section className="arena">
        {renderPanel("Player Panel", "player", playerState, "#e76f51")}
        {renderPanel("Agent Panel", "agent", agentState, "#2a9d8f")}
      </section>

      <section className="footer-bar">
        <div className="history-card">
          <h3>Round Log</h3>
          {history.length === 0 ? (
            <p>No rounds have finished yet. Start from the left keyboard.</p>
          ) : (
            <ul>
              {history.map((item) => (
                <li key={item.round}>
                  Round {item.round}, player `{item.playerWord}` vs AI `{item.agentWord}`: {item.winner}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="action-card">
          <h3>{matchFinished ? "Match Complete" : "Rules"}</h3>
          <p>
            Both sides keep separate progress on different answer words. The result first compares solved vs unsolved,
            then fewer mistakes, then fewer total steps.
          </p>
          <button type="button" className="restart" onClick={resetMatch}>
            {matchFinished ? "Restart Match" : "Reset Match"}
          </button>
        </div>
      </section>
    </main>
  );
}

export default App;
