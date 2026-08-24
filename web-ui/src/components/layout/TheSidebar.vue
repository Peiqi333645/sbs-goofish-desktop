<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { LayoutDashboard, ListTodo, Users, Layers, Terminal, Settings2, ChevronRight } from 'lucide-vue-next'
import { useWebSocket } from '@/composables/useWebSocket'
import { useI18n } from 'vue-i18n'
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
    <div class="mt-12 px-4">
      <div class="rounded-2xl border border-dashed border-white/10 bg-white/[.04] p-4">
        <p class="mb-2 text-[9px] font-black uppercase tracking-[.2em] text-white/35">{{ t('sidebar.systemStatus') }}</p>
        <div class="flex items-center gap-2"><div class="h-2 w-2 rounded-full" :class="connectionTone"></div><span class="text-xs font-bold text-white/65">{{ connectionLabel }}</span></div>
      </div>
    </div>
  </nav>
</template>
