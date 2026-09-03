<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { LayoutDashboard, ListTodo, Users, Layers, Terminal, Settings2, ChevronRight } from 'lucide-vue-next'
import { useWebSocket } from '@/composables/useWebSocket'
import { useI18n } from 'vue-i18n'
import { getTaskProgress } from '@/api/tasks'
import type { TaskProgress } from '@/types/task.d.ts'
const emit = defineEmits<{ (event: 'navigate'): void }>()
const { isConnected } = useWebSocket()
const { t } = useI18n()
const navItems = computed(() => [
  { to: '/dashboard', label: t('sidebar.dashboard'), icon: LayoutDashboard },
  { to: '/tasks', label: t('sidebar.tasks'), icon: ListTodo },
  { to: '/accounts', label: t('sidebar.accounts'), icon: Users },
  { to: '/results', label: t('sidebar.results'), icon: Layers },
  { to: '/logs', label: t('sidebar.logs'), icon: Terminal },
  { to: '/settings', label: t('sidebar.settings'), icon: Settings2 },
])
const connectionLabel = computed(() => isConnected.value ? t('sidebar.backendConnected') : t('sidebar.backendConnecting'))
const connectionTone = computed(() => isConnected.value ? 'bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,.55)]' : 'bg-primary shadow-[0_0_10px_rgba(255,172,0,.55)]')
const taskProgress = ref<TaskProgress[]>([])
let progressTimer: ReturnType<typeof setInterval> | undefined

async function refreshProgress() {
  try {
    taskProgress.value = await getTaskProgress()
  } catch {
    // Connection state already communicates backend availability.
  }
}

function stageLabel(progress: TaskProgress) {
  if (progress.stage === 'scraping') return t('sidebar.progressScraping')
  if (progress.stage === 'analyzing') return t('sidebar.progressAnalyzing')
  if (progress.stage === 'completed') return t('sidebar.progressCompleted')
  if (progress.stage === 'failed') return t('sidebar.progressFailed')
  return t('sidebar.progressIdle')
}

onMounted(() => {
  refreshProgress()
  progressTimer = setInterval(refreshProgress, 2000)
})
onUnmounted(() => progressTimer && clearInterval(progressTimer))
</script>

<template>
  <nav class="space-y-1">
    <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" v-slot="{ isActive }" class="group relative flex items-center overflow-hidden rounded-xl px-4 py-3 transition-all duration-200" @click="emit('navigate')">
      <div v-if="isActive" class="absolute inset-0 z-0 bg-gradient-to-r from-primary/20 to-transparent"></div>
      <div v-if="isActive" class="absolute left-0 top-1/2 h-7 w-1 -translate-y-1/2 rounded-r-full bg-primary"></div>
      <div class="relative z-10 flex w-full items-center">
        <component :is="item.icon" class="mr-3 h-5 w-5 transition-colors" :class="isActive ? 'text-primary' : 'text-white/40 group-hover:text-white/70'" />
        <span class="flex-grow text-sm font-bold transition-colors" :class="isActive ? 'text-white' : 'text-white/55 group-hover:text-white'">{{ item.label }}</span>
        <ChevronRight v-if="isActive" class="h-4 w-4 text-primary" />
      </div>
    </RouterLink>
    <div class="mt-8 px-4">
      <div class="rounded-2xl border border-dashed border-white/10 bg-white/[.04] p-4">
        <p class="mb-2 text-[9px] font-black uppercase tracking-[.2em] text-white/35">{{ t('sidebar.systemStatus') }}</p>
        <div class="flex items-center gap-2"><div class="h-2 w-2 rounded-full" :class="connectionTone"></div><span class="text-xs font-bold text-white/65">{{ connectionLabel }}</span></div>
      </div>
      <div class="mt-4">
        <div class="mb-2 flex items-center justify-between px-1">
          <p class="text-[9px] font-black uppercase tracking-[.2em] text-white/35">{{ t('sidebar.taskProgress') }}</p>
          <span class="text-[9px] font-bold text-white/25">{{ taskProgress.length }}</span>
        </div>
        <div class="max-h-[calc(100vh-31rem)] min-h-16 space-y-2 overflow-y-auto pr-1 [scrollbar-color:rgba(255,172,0,.35)_transparent] [scrollbar-width:thin]">
          <div v-if="!taskProgress.length" class="rounded-xl border border-white/[.06] bg-white/[.025] px-3 py-3 text-[10px] text-white/30">
            {{ t('sidebar.noTasks') }}
          </div>
          <div v-for="progress in taskProgress" :key="progress.task_id" class="rounded-xl border border-white/[.07] bg-white/[.04] px-3 py-2.5">
            <div class="flex items-center justify-between gap-2">
              <span class="truncate text-[11px] font-bold text-white/70">{{ progress.task_name }}</span>
              <span class="shrink-0 text-[9px] font-bold" :class="progress.stage === 'failed' ? 'text-rose-400' : progress.is_running ? 'text-primary' : 'text-white/30'">{{ stageLabel(progress) }}</span>
            </div>
            <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-white/[.07]">
              <div class="h-full rounded-full transition-all duration-500" :class="progress.stage === 'failed' ? 'bg-rose-400' : 'bg-gradient-to-r from-primary/70 to-primary'" :style="{ width: `${progress.percent}%` }"></div>
            </div>
            <div class="mt-1.5 flex items-center justify-between text-[9px] text-white/35">
              <span>{{ t('sidebar.pageProgress', { current: progress.page || 0, total: progress.max_pages }) }}</span>
              <span>{{ progress.percent }}%</span>
            </div>
            <div v-if="progress.is_running" class="mt-1 truncate text-[9px] text-white/30">
              {{ t('sidebar.itemProgress', { matched: progress.matched_count, detailed: progress.detail_completed }) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>
