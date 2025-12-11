<script lang="ts">
  import { currentTurn, waterfallData, computedStats, latencyStats } from '../stores';
  import { formatDuration } from '../utils';

  // Use current turn if active, otherwise preserved waterfall data
  let data = $derived($currentTurn.active ? $currentTurn : $waterfallData);

  interface BarStyle {
    left: string;
    width: string;
    opacity: number;
  }

  function getBarStyle(
    baseTime: number,
    totalDuration: number,
    startTs: number | null,
    endTs: number | null,
    isActiveNow: boolean
  ): BarStyle {
    if (!startTs) return { left: '0%', width: '0%', opacity: 0 };

    const now = Date.now();
    const left = ((startTs - baseTime) / totalDuration) * 100;

    let end: number;
    if (endTs) {
      end = endTs;
    } else if (isActiveNow) {
      end = now;
    } else {
      end = startTs;
    }

    const width = Math.max(((end - startTs) / totalDuration) * 100, 0.5);
    return { left: `${left}%`, width: `${width}%`, opacity: 1 };
  }

  function getDuration(startTs: number | null, endTs: number | null, isActiveNow: boolean): string {
    if (!startTs) return '—';
    if (!endTs && isActiveNow) return formatDuration(Date.now() - startTs);
    if (!endTs) return '—';
    return formatDuration(endTs - startTs);
  }

  let bars = $derived.by(() => {
    if (!data?.turnStartTs) return null;

    const baseTime = data.turnStartTs;
    const now = Date.now();
    const isActive = $currentTurn.active;

    // Calculate end time for scaling
    let endTime = baseTime;
    if (data.ttsEndTs) endTime = Math.max(endTime, data.ttsEndTs);
    else if (data.agentEndTs) endTime = Math.max(endTime, data.agentEndTs);
    else if (data.sttEndTs) endTime = Math.max(endTime, data.sttEndTs);
    if (isActive) endTime = Math.max(endTime, now);

    const totalDuration = Math.max(endTime - baseTime, 500);

    return {
      stt: {
        style: getBarStyle(baseTime, totalDuration, data.sttStartTs, data.sttEndTs, isActive && !!data.sttStartTs && !data.sttEndTs),
        duration: getDuration(data.sttStartTs, data.sttEndTs, isActive && !!data.sttStartTs && !data.sttEndTs),
      },
      agent: {
        style: getBarStyle(baseTime, totalDuration, data.agentStartTs, data.agentEndTs, isActive && !!data.agentStartTs && !data.agentEndTs),
        duration: getDuration(data.agentStartTs, data.agentEndTs, isActive && !!data.agentStartTs && !data.agentEndTs),
      },
      tts: {
        style: getBarStyle(baseTime, totalDuration, data.ttsStartTs, data.ttsEndTs, isActive && !!data.ttsStartTs && !data.ttsEndTs),
        duration: getDuration(data.ttsStartTs, data.ttsEndTs, isActive && !!data.ttsStartTs && !data.ttsEndTs),
      },
    };
  });

  let totalLatencyDisplay = $derived.by(() => {
    if (!data) return '—';
    if (data.sttStartTs && data.ttsEndTs) {
      return formatDuration(data.ttsEndTs - data.sttStartTs);
    }
    if ($currentTurn.active && data.sttStartTs) {
      return formatDuration(Date.now() - data.sttStartTs);
    }
    return '—';
  });
</script>

<div class="mt-6 pt-6 border-t border-slate-700/50">
  <!-- Header -->
  <div class="flex items-center gap-2.5 mb-5">
    <div class="w-6 h-6 rounded-md bg-amber-500/15 flex items-center justify-center">
      <svg class="w-3.5 h-3.5 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
      </svg>
    </div>
    <span class="text-xs font-semibold uppercase tracking-widest text-slate-400">Latency Analysis</span>
    <span class="ml-auto font-mono text-sm font-bold text-emerald-400">{totalLatencyDisplay}</span>
  </div>

  <!-- Waterfall Bars -->
  <div class="mb-5">
    {#if bars}
      {#each [
        { label: 'STT', bar: bars.stt, gradient: 'from-emerald-400 to-teal-500' },
        { label: 'Agent', bar: bars.agent, gradient: 'from-violet-500 to-purple-600' },
        { label: 'TTS', bar: bars.tts, gradient: 'from-amber-400 to-orange-500' },
      ] as row}
        <div class="flex items-center mb-2.5">
          <div class="w-14 flex-shrink-0 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
            {row.label}
          </div>
          <div class="flex-1 h-6 bg-slate-800/80 rounded-md relative overflow-hidden border border-slate-700/30">
            <div
              class="absolute h-full rounded-md bg-gradient-to-r {row.gradient} min-w-0.5 transition-all duration-150"
              style="left: {row.bar.style.left}; width: {row.bar.style.width}; opacity: {row.bar.style.opacity}"
            ></div>
          </div>
          <div class="w-16 flex-shrink-0 text-right font-mono text-xs text-slate-400 pl-3">
            {row.bar.duration}
          </div>
        </div>
      {/each}
    {:else}
      <div class="text-center py-6 text-slate-500 text-sm">Latency metrics will appear here during research</div>
    {/if}
  </div>

  <!-- Stats Row -->
  <div class="grid grid-cols-4 gap-3 pt-4 border-t border-slate-700/50">
    <div class="flex flex-col items-center gap-1.5 py-2 px-3 bg-slate-800/40 rounded-lg">
      <span class="text-[9px] font-semibold uppercase tracking-widest text-slate-500">Queries</span>
      <span class="font-mono text-base font-bold text-slate-300">{$latencyStats.turns}</span>
    </div>
    <div class="flex flex-col items-center gap-1.5 py-2 px-3 bg-slate-800/40 rounded-lg">
      <span class="text-[9px] font-semibold uppercase tracking-widest text-slate-500">Avg</span>
      <span class="font-mono text-base font-bold text-slate-300">{$computedStats.avg ? formatDuration($computedStats.avg) : '—'}</span>
    </div>
    <div class="flex flex-col items-center gap-1.5 py-2 px-3 bg-slate-800/40 rounded-lg">
      <span class="text-[9px] font-semibold uppercase tracking-widest text-slate-500">Min</span>
      <span class="font-mono text-base font-bold text-emerald-400">{$computedStats.min ? formatDuration($computedStats.min) : '—'}</span>
    </div>
    <div class="flex flex-col items-center gap-1.5 py-2 px-3 bg-slate-800/40 rounded-lg">
      <span class="text-[9px] font-semibold uppercase tracking-widest text-slate-500">Max</span>
      <span class="font-mono text-base font-bold text-amber-400">{$computedStats.max ? formatDuration($computedStats.max) : '—'}</span>
    </div>
  </div>
</div>
