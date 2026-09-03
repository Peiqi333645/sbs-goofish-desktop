<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import DashboardTaskSearch from '@/components/layout/DashboardTaskSearch.vue'
import LocaleToggle from '@/components/layout/LocaleToggle.vue'
import { Bell, Search, UserCircle, HelpCircle, Menu } from 'lucide-vue-next'
import Badge from '@/components/ui/badge/Badge.vue'
import { useMobileNav } from '@/composables/useMobileNav'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const route = useRoute()
const { toggleMobileNav } = useMobileNav()
const inactiveSearchValue = ref('')
const { t } = useI18n()
const isDashboard = computed(() => route.name === 'Dashboard')
const goAccounts = () => router.push('/accounts')
const goNotifications = () => router.push({ name: 'Settings', query: { tab: 'notifications' } })
const goPrompts = () => router.push({ name: 'Settings', query: { tab: 'prompts' } })
</script>

<template>
  <header class="sticky top-0 z-[100] flex h-16 items-center justify-between border-b border-amber-400/20 bg-[#222222]/95 px-6 text-white backdrop-blur-xl">
    <RouterLink to="/dashboard" class="group flex items-center gap-3 rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary" :aria-label="t('header.goHome')">
      <img src="/favicon.png" alt="" class="brand-grid h-9 w-9 rounded-xl transition-transform group-hover:scale-105" />
      <div>
        <h1 class="text-[15px] font-black tracking-wide text-white">SBS<span class="text-primary">闲鱼助手</span></h1>
        <p class="text-[9px] font-semibold tracking-[.24em] text-white/45">SMART MONITOR</p>
      </div>
      <Badge variant="outline" class="ml-1 hidden border-primary/35 bg-primary/10 text-[9px] font-black text-primary sm:flex">DESKTOP</Badge>
    </RouterLink>
    <div class="mx-8 hidden max-w-md flex-grow md:flex">
      <DashboardTaskSearch v-if="isDashboard" />
      <div v-else class="group relative w-full">
        <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/35" />
        <input v-model="inactiveSearchValue" readonly aria-disabled="true" :placeholder="t('header.searchUnavailable')" class="h-10 w-full rounded-xl border border-white/10 bg-white/5 pl-10 pr-4 text-sm text-white placeholder:text-white/35 focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/20" />
      </div>
    </div>
    <div class="flex items-center gap-2">
      <LocaleToggle />
      <Button variant="ghost" size="icon" class="rounded-full text-white/65 hover:bg-primary/15 hover:text-primary" :aria-label="t('header.openNotifications')" @click="goNotifications"><Bell class="h-5 w-5" /></Button>
      <Button variant="ghost" size="icon" class="rounded-full text-white/65 hover:bg-primary/15 hover:text-primary" :aria-label="t('header.openPrompts')" @click="goPrompts"><HelpCircle class="h-5 w-5" /></Button>
      <div class="mx-1 hidden h-6 w-px bg-white/15 sm:block"></div>
      <Button variant="ghost" class="hidden items-center gap-2 rounded-full text-white hover:bg-white/10 sm:flex" :aria-label="t('header.openAccounts')" @click="goAccounts">
        <div class="flex h-8 w-8 items-center justify-center rounded-full border border-primary/30 bg-primary/15"><UserCircle class="h-6 w-6 text-primary" /></div>
        <div class="hidden text-left lg:block"><p class="text-xs font-black leading-none">SBS Admin</p><p class="mt-1 text-[9px] text-white/45">{{ t('header.accountManagement') }}</p></div>
      </Button>
      <Button variant="ghost" size="icon" class="text-white md:hidden" :aria-label="t('header.openNavigation')" @click="toggleMobileNav"><Menu class="h-6 w-6" /></Button>
    </div>
  </header>
</template>
