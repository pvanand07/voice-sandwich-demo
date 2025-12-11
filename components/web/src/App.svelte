<script lang="ts">
  import { Header, Controls, PipelineCard, ActivityFeed, Console } from './lib/components';
  import { createVoiceSession } from './lib/websocket';

  const voiceSession = createVoiceSession();
</script>

<div class="max-w-3xl mx-auto px-4 pb-12">
  <Header />
  <Controls onStart={() => voiceSession.start()} onStop={() => voiceSession.stop()} />
  <ActivityFeed />
  <PipelineCard />
  <Console />
  
  <!-- Footer -->
  <div class="mt-8 text-center">
    <p class="text-xs text-slate-600">
      <span class="text-slate-500">iresearcher</span> • Intelligent AI Research Engine
    </p>
  </div>
</div>
