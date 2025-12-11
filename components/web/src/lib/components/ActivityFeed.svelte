<script lang="ts">
  import { activities } from '../stores';
  import { formatTime } from '../utils';

  const iconMap: Record<string, string> = {
    stt: '🎤',
    agent: '🤖',
    tts: '🔊',
    tool: '🔧',
  };

  const colorMap: Record<string, { bg: string; label: string; border: string }> = {
    stt: { bg: 'bg-emerald-500/10', label: 'text-emerald-400', border: 'border-emerald-500/20' },
    agent: { bg: 'bg-violet-500/10', label: 'text-violet-400', border: 'border-violet-500/20' },
    tts: { bg: 'bg-amber-500/10', label: 'text-amber-400', border: 'border-amber-500/20' },
    tool: { bg: 'bg-blue-500/10', label: 'text-blue-400', border: 'border-blue-500/20' },
  };
</script>

<div class="glass rounded-2xl p-6 mb-6">
  <div class="flex items-center justify-between mb-5">
    <div class="flex items-center gap-2.5">
      <div class="w-8 h-8 rounded-lg bg-emerald-500/15 flex items-center justify-center">
        <svg class="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9"></path>
          <path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854z"></path>
        </svg>
      </div>
      <span class="text-xs font-semibold uppercase tracking-widest text-slate-400">Research Activity</span>
    </div>
    <button
      onclick={() => activities.clear()}
      class="text-xs text-slate-500 hover:text-slate-300 transition-colors cursor-pointer px-3 py-1.5 rounded-lg hover:bg-slate-800/60"
    >
      Clear
    </button>
  </div>

  <div class="max-h-80 overflow-y-auto flex flex-col gap-3">
    {#if $activities.length === 0}
      <div class="text-slate-500 text-sm py-8 text-center flex flex-col items-center gap-2">
        <svg class="w-8 h-8 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.3-4.3"></path>
        </svg>
        <span>No research activity yet...</span>
      </div>
    {:else}
      {#each $activities as item (item.id)}
        <div class="flex items-start gap-3 p-4 bg-slate-800/50 rounded-xl border {colorMap[item.type]?.border || 'border-slate-700/50'} animate-slideIn">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center text-base flex-shrink-0 {colorMap[item.type]?.bg}">
            {iconMap[item.type] || '📋'}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-[10px] font-semibold uppercase tracking-widest mb-1 {colorMap[item.type]?.label}">
              {item.label}
            </div>
            <div class="text-sm text-slate-200 leading-relaxed break-words">{item.text}</div>
            {#if item.args}
              <pre class="mt-2.5 p-3 bg-slate-900/60 rounded-lg font-mono text-[11px] text-slate-400 overflow-x-auto whitespace-pre-wrap border border-slate-700/30">{JSON.stringify(item.args, null, 2)}</pre>
            {/if}
            <div class="mt-2">
              <span class="font-mono text-[10px] text-slate-500">{formatTime(item.timestamp)}</span>
            </div>
          </div>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-slideIn {
    animation: slideIn 0.3s ease-out;
  }
</style>
