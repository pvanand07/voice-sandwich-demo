<script lang="ts">
  import { currentTurn } from '../stores';
  import { formatDuration } from '../utils';

  interface StageState {
    active: boolean;
    complete: boolean;
    time: string;
  }

  let stt = $derived<StageState>({
    active: !!$currentTurn.sttStartTs && !$currentTurn.sttEndTs,
    complete: !!$currentTurn.sttEndTs,
    time: $currentTurn.sttEndTs && $currentTurn.sttStartTs
      ? formatDuration($currentTurn.sttEndTs - $currentTurn.sttStartTs)
      : $currentTurn.sttStartTs ? '...' : '—',
  });

  let agent = $derived<StageState>({
    active: !!$currentTurn.agentStartTs && !$currentTurn.agentEndTs,
    complete: !!$currentTurn.agentEndTs,
    time: $currentTurn.agentEndTs && $currentTurn.agentStartTs
      ? formatDuration($currentTurn.agentEndTs - $currentTurn.agentStartTs)
      : $currentTurn.agentStartTs ? '...' : '—',
  });

  let tts = $derived<StageState>({
    active: !!$currentTurn.ttsStartTs && !$currentTurn.ttsEndTs,
    complete: !!$currentTurn.ttsEndTs,
    time: $currentTurn.ttsEndTs && $currentTurn.ttsStartTs
      ? formatDuration($currentTurn.ttsEndTs - $currentTurn.ttsStartTs)
      : $currentTurn.ttsStartTs ? '...' : '—',
  });

  type ColorTheme = 'emerald' | 'violet' | 'amber';
  
  const colorConfig: Record<ColorTheme, { border: string; active: string; icon: string }> = {
    emerald: {
      border: 'border-emerald-500/50',
      active: 'bg-emerald-500/20 shadow-[0_0_24px_theme(colors.emerald.500/40)]',
      icon: 'text-emerald-400',
    },
    violet: {
      border: 'border-violet-500/50',
      active: 'bg-violet-500/20 shadow-[0_0_24px_theme(colors.violet.500/40)]',
      icon: 'text-violet-400',
    },
    amber: {
      border: 'border-amber-500/50',
      active: 'bg-amber-500/20 shadow-[0_0_24px_theme(colors.amber.500/40)]',
      icon: 'text-amber-400',
    },
  };

  function stageClasses(state: StageState, color: ColorTheme): string {
    const c = colorConfig[color];
    let classes = `w-16 h-16 rounded-xl flex items-center justify-center
                   bg-slate-800/80 border-2 ${c.border} transition-all duration-300`;

    if (state.active) {
      classes += ` ${c.active} scale-110`;
    } else if (state.complete) {
      classes += ' opacity-60';
    }

    return classes;
  }
</script>

<div class="flex items-center justify-center gap-3 py-6">
  <!-- STT Stage -->
  <div class="flex flex-col items-center gap-3">
    <div class={stageClasses(stt, 'emerald')}>
      <svg class="w-7 h-7 {colorConfig.emerald.icon}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
        <line x1="12" x2="12" y1="19" y2="22"></line>
      </svg>
    </div>
    <div class="text-[10px] font-semibold uppercase tracking-widest text-slate-500">Transcribe</div>
    <div class="font-mono text-xs text-slate-400">{stt.time}</div>
  </div>

  <!-- Arrow -->
  <div class="flex items-center justify-center w-8 -mt-8">
    <svg class="w-5 h-5 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M5 12h14m-7-7 7 7-7 7"></path>
    </svg>
  </div>

  <!-- Agent Stage -->
  <div class="flex flex-col items-center gap-3">
    <div class={stageClasses(agent, 'violet')}>
      <svg class="w-7 h-7 {colorConfig.violet.icon}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 8V4H8"></path>
        <rect width="16" height="12" x="4" y="8" rx="2"></rect>
        <path d="M2 14h2"></path>
        <path d="M20 14h2"></path>
        <path d="M15 13v2"></path>
        <path d="M9 13v2"></path>
      </svg>
    </div>
    <div class="text-[10px] font-semibold uppercase tracking-widest text-slate-500">Analyze</div>
    <div class="font-mono text-xs text-slate-400">{agent.time}</div>
  </div>

  <!-- Arrow -->
  <div class="flex items-center justify-center w-8 -mt-8">
    <svg class="w-5 h-5 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M5 12h14m-7-7 7 7-7 7"></path>
    </svg>
  </div>

  <!-- TTS Stage -->
  <div class="flex flex-col items-center gap-3">
    <div class={stageClasses(tts, 'amber')}>
      <svg class="w-7 h-7 {colorConfig.amber.icon}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z"></path>
        <path d="M16 9a5 5 0 0 1 0 6"></path>
        <path d="M19.364 18.364a9 9 0 0 0 0-12.728"></path>
      </svg>
    </div>
    <div class="text-[10px] font-semibold uppercase tracking-widest text-slate-500">Synthesize</div>
    <div class="font-mono text-xs text-slate-400">{tts.time}</div>
  </div>
</div>
