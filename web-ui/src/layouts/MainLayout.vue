<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import TheHeader from '@/components/layout/TheHeader.vue'
import TheSidebar from '@/components/layout/TheSidebar.vue'
import { useMobileNav } from '@/composables/useMobileNav'
const { isMobileNavOpen, closeMobileNav } = useMobileNav()
const { t } = useI18n()
</script>

<template>
  <div class="relative flex min-h-screen w-full flex-col bg-background selection:bg-primary/30">
    <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[120] focus:rounded-lg focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-primary-foreground">{{ t('common.skipToContent') }}</a>
    <div aria-hidden="true" class="pointer-events-none fixed inset-0 overflow-hidden">
      <div class="absolute -left-[12%] -top-[18%] h-[48%] w-[48%] rounded-full bg-primary/10 blur-[130px]"></div>
      <div class="absolute -bottom-[15%] right-[8%] h-[38%] w-[38%] rounded-full bg-neutral-900/5 blur-[110px]"></div>
    </div>
    <TheHeader />
    <transition name="mobile-nav">
      <div v-if="isMobileNavOpen" class="fixed inset-0 z-[90] md:hidden">
        <button type="button" class="absolute inset-0 bg-black/45 backdrop-blur-[2px]" :aria-label="t('common.close')" @click="closeMobileNav" />
        <aside class="relative h-full w-72 border-r border-primary/15 bg-[#222222] p-4 shadow-2xl"><TheSidebar class="pt-16" @navigate="closeMobileNav" /></aside>
      </div>
    </transition>
    <div class="relative z-10 flex flex-grow">
      <aside class="hidden w-64 flex-shrink-0 border-r border-primary/10 bg-[#222222] md:block">
        <TheSidebar class="sticky top-16 h-[calc(100vh-4rem)] p-4" />
      </aside>
      <main id="main-content" tabindex="-1" class="flex-grow overflow-x-hidden p-4 focus:outline-none md:p-8">
        <div class="mx-auto max-w-7xl animate-fade-in">
          <RouterView v-slot="{ Component }"><transition name="page" mode="out-in"><component :is="Component" /></transition></RouterView>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.page-enter-active,.page-leave-active,.mobile-nav-enter-active,.mobile-nav-leave-active{transition:opacity .2s ease,transform .2s ease}
.page-enter-from{opacity:0;transform:translateY(10px)}
.page-leave-to{opacity:0;transform:translateY(-10px)}
.mobile-nav-enter-from,.mobile-nav-leave-to{opacity:0;transform:translateX(-12px)}
@media(prefers-reduced-motion:reduce){.page-enter-active,.page-leave-active,.mobile-nav-enter-active,.mobile-nav-leave-active{transition:none}.page-enter-from,.page-leave-to,.mobile-nav-enter-from,.mobile-nav-leave-to{opacity:1;transform:none}}
</style>
