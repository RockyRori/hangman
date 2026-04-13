import json
import pickle
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
Q_TABLE_SOURCE = ROOT / "backend" / "q_table.pkl"
WORD_SOURCE = ROOT / "shared" / "words.json"
TARGET_DIR = ROOT / "frontend" / "public"
Q_TABLE_TARGET = TARGET_DIR / "q-table.json"
WORD_TARGET = TARGET_DIR / "words.json"


def sync_qtable() -> None:
    if not Q_TABLE_SOURCE.exists():
        raise FileNotFoundError(f"Missing q_table file: {Q_TABLE_SOURCE}")

    with Q_TABLE_SOURCE.open("rb") as handle:
        q_table = pickle.load(handle)

    serializable = {
        f"{state}|{action}": float(value)
        for (state, action), value in q_table.items()
    }

    with Q_TABLE_TARGET.open("w", encoding="utf-8") as handle:
        json.dump(serializable, handle, ensure_ascii=False, separators=(",", ":"))

    print(f"Synced {len(serializable)} Q entries to {Q_TABLE_TARGET}")


def sync_words() -> None:
    if not WORD_SOURCE.exists():
        raise FileNotFoundError(f"Missing shared words file: {WORD_SOURCE}")

    words = json.loads(WORD_SOURCE.read_text(encoding="utf-8"))
    with WORD_TARGET.open("w", encoding="utf-8") as handle:
        json.dump(words, handle, ensure_ascii=False, separators=(",", ":"))

    print(f"Synced {len(words)} shared words to {WORD_TARGET}")


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    sync_qtable()
    sync_words()


if __name__ == "__main__":
    main()
