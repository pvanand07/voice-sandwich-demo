<script lang="ts">
  import { session, formattedTime } from '../stores';
</script>

<header class="flex items-center justify-between mb-8 pt-6">
  <div class="flex items-center gap-4">
    <!-- Logo mark -->
    <div class="relative w-12 h-12 flex items-center justify-center">
      <div class="absolute inset-0 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl rotate-3 opacity-80"></div>
      <div class="absolute inset-0 bg-slate-900 rounded-xl flex items-center justify-center">
        <svg class="w-6 h-6 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.3-4.3"></path>
          <path d="M11 8v6"></path>
          <path d="M8 11h6"></path>
        </svg>
      </div>
    </div>
    
    <div class="flex flex-col">
      <h1 class="text-2xl font-bold tracking-tight">
        <span class="text-gradient">iresearcher</span>
      </h1>
      <span class="text-xs text-slate-500 tracking-widest uppercase">Intelligent AI Research Engine</span>
    </div>
  </div>
  
  <div class="flex items-center gap-4">
    <div class="flex items-center gap-2 font-mono text-sm text-slate-500 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-slate-700/50">
      <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
      </svg>
      <span>{$formattedTime}</span>
    </div>
    <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg border
                {$session.connected 
                  ? 'bg-emerald-500/10 border-emerald-500/30' 
                  : 'bg-slate-800/50 border-slate-700/50'}">
      <span
        class="w-2 h-2 rounded-full transition-all duration-300 {$session.connected
          ? 'bg-emerald-400 shadow-[0_0_8px_theme(colors.emerald.400)]'
          : 'bg-slate-600'}"
      ></span>
      <span class="text-xs font-medium {$session.connected ? 'text-emerald-400' : 'text-slate-500'}">
        {$session.connected ? 'Connected' : 'Offline'}
      </span>
    </div>
  </div>
</header>
