<script lang="ts">
  import { session } from '../stores';

  interface Props {
    onStart: () => void;
    onStop: () => void;
  }

  let { onStart, onStop }: Props = $props();
</script>

<div class="glass rounded-2xl p-6 mb-6">
  <div class="flex gap-3 mb-5">
    <button
      onclick={onStart}
      disabled={$session.connected}
      class="flex-1 py-4 px-6 text-sm font-semibold rounded-xl
             flex items-center justify-center gap-2.5 transition-all duration-300
             bg-gradient-to-r from-emerald-600 to-teal-600 text-white
             hover:from-emerald-500 hover:to-teal-500 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-emerald-500/25
             disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.3-4.3"></path>
      </svg>
      Start Research
    </button>
    <button
      onclick={onStop}
      disabled={!$session.connected}
      class="flex-1 py-4 px-6 text-sm font-semibold rounded-xl
             flex items-center justify-center gap-2 transition-all duration-300
             bg-slate-800 text-slate-300 border border-slate-700
             hover:bg-slate-700 hover:border-slate-600 hover:text-white
             disabled:opacity-40 disabled:cursor-not-allowed"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <rect x="6" y="6" width="12" height="12" rx="2"></rect>
      </svg>
      End Session
    </button>
  </div>
</div>
