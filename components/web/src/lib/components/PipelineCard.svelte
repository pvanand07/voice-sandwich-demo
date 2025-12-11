<script lang="ts">
  import { currentTurn } from '../stores';
  import Pipeline from './Pipeline.svelte';
  import LatencyWaterfall from './LatencyWaterfall.svelte';
</script>

<div
  class="glass rounded-2xl p-6 mb-6 transition-all duration-300
         {$currentTurn.active ? 'border-emerald-500/30 glow-emerald' : ''}"
>
  <div class="flex items-center justify-between mb-5">
    <div class="flex items-center gap-2.5">
      <div class="w-8 h-8 rounded-lg bg-violet-500/15 flex items-center justify-center">
        <svg class="w-4 h-4 text-violet-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 3v3m6.366-.366-2.12 2.12M21 12h-3m.366 6.366-2.12-2.12M12 21v-3m-6.366.366 2.12-2.12M3 12h3m-.366-6.366 2.12 2.12"></path>
        </svg>
      </div>
      <span class="text-xs font-semibold uppercase tracking-widest text-slate-400">Research Pipeline</span>
    </div>
    <span
      class="font-mono text-xs py-1.5 px-3 rounded-lg transition-all duration-300
             {$currentTurn.active
               ? 'text-emerald-400 bg-emerald-500/15 border border-emerald-500/30'
               : 'text-slate-500 bg-slate-800/60 border border-slate-700/50'}"
    >
      {$currentTurn.active ? '● Processing' : '○ Standby'}
    </span>
  </div>

  <Pipeline />
  <LatencyWaterfall />
</div>
