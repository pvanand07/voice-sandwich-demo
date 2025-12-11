<script lang="ts">
  import { logs } from '../stores';
  import { formatTime } from '../utils';
</script>

<div class="glass rounded-2xl p-6">
  <div class="flex items-center justify-between mb-5">
    <div class="flex items-center gap-2.5">
      <div class="w-8 h-8 rounded-lg bg-slate-700/60 flex items-center justify-center">
        <svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="4 17 10 11 4 5"></polyline>
          <line x1="12" x2="20" y1="19" y2="19"></line>
        </svg>
      </div>
      <span class="text-xs font-semibold uppercase tracking-widest text-slate-400">Console</span>
    </div>
    <div class="flex items-center gap-1.5">
      <span class="w-2 h-2 rounded-full bg-emerald-500/60"></span>
      <span class="w-2 h-2 rounded-full bg-amber-500/60"></span>
      <span class="w-2 h-2 rounded-full bg-red-500/60"></span>
    </div>
  </div>

  <div class="max-h-48 overflow-y-auto font-mono text-[11px] text-slate-400 leading-relaxed bg-slate-900/50 rounded-xl p-4 border border-slate-700/30">
    {#if $logs.length === 0}
      <div class="text-slate-600 flex items-center gap-2">
        <span class="text-emerald-500">❯</span>
        <span class="animate-pulse">System logs will appear here...</span>
      </div>
    {:else}
      {#each $logs as entry (entry.id)}
        <div class="py-1 border-b border-slate-800/50 last:border-b-0 flex items-start gap-2">
          <span class="text-emerald-500/70 flex-shrink-0">❯</span>
          <span class="text-slate-600 flex-shrink-0">{formatTime(entry.timestamp)}</span>
          <span class="text-slate-300">{entry.message}</span>
        </div>
      {/each}
    {/if}
  </div>
</div>
