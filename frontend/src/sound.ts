type SoundKind = "guess" | "success" | "failure";

const clampTime = (value: number) => Math.max(value, 0.001);

export class SoundBoard {
  private context: AudioContext | null = null;

  private getContext(): AudioContext | null {
    if (typeof window === "undefined") {
      return null;
    }

    const AudioCtor = window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!AudioCtor) {
      return null;
    }

    if (!this.context) {
      this.context = new AudioCtor();
    }

    if (this.context.state === "suspended") {
      void this.context.resume();
    }

    return this.context;
  }

  private pulse(
    context: AudioContext,
    frequency: number,
    duration: number,
    startAt: number,
    type: OscillatorType,
    gainValue: number
  ) {
    const oscillator = context.createOscillator();
    const gain = context.createGain();

    oscillator.type = type;
    oscillator.frequency.setValueAtTime(frequency, startAt);

    gain.gain.setValueAtTime(0.0001, startAt);
    gain.gain.exponentialRampToValueAtTime(gainValue, startAt + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, startAt + clampTime(duration));

    oscillator.connect(gain);
    gain.connect(context.destination);

    oscillator.start(startAt);
    oscillator.stop(startAt + clampTime(duration) + 0.02);
  }

  private shimmer(context: AudioContext, startAt: number, frequencies: number[]) {
    frequencies.forEach((frequency, index) => {
      this.pulse(context, frequency, 0.34 + index * 0.03, startAt + index * 0.08, "triangle", 0.032);
    });
  }

  play(kind: SoundKind) {
    const context = this.getContext();
    if (!context) {
      return;
    }

    const startAt = context.currentTime;

    if (kind === "guess") {
      this.pulse(context, 520, 0.08, startAt, "triangle", 0.05);
      this.pulse(context, 660, 0.09, startAt + 0.05, "triangle", 0.04);
      return;
    }

    if (kind === "success") {
      this.pulse(context, 523.25, 0.22, startAt, "sine", 0.055);
      this.pulse(context, 659.25, 0.26, startAt + 0.1, "sine", 0.058);
      this.pulse(context, 783.99, 0.32, startAt + 0.22, "sine", 0.06);
      this.pulse(context, 1046.5, 0.42, startAt + 0.4, "sine", 0.05);
      this.shimmer(context, startAt + 0.18, [783.99, 987.77, 1174.66, 1318.51]);
      return;
    }

    this.pulse(context, 392, 0.14, startAt, "sawtooth", 0.045);
    this.pulse(context, 293.66, 0.18, startAt + 0.12, "sawtooth", 0.05);
    this.pulse(context, 196, 0.24, startAt + 0.24, "sawtooth", 0.05);
  }
}
