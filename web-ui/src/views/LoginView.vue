<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import LocaleToggle from '@/components/layout/LocaleToggle.vue'
import BrandIcon from '@/assets/sbs-brand.svg'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardFooter } from '@/components/ui/card'
import { useI18n } from 'vue-i18n'
const username=ref(''), password=ref(''), isLoading=ref(false), error=ref('')
const { login }=useAuth(), router=useRouter(), route=useRoute(), { t }=useI18n()
async function handleLogin(){
 if(!username.value||!password.value){error.value=t('login.errors.missingCredentials');return}
 isLoading.value=true;error.value=''
 try{const success=await login(username.value,password.value);if(success)router.push((route.query.redirect as string)||'/');else error.value=t('login.errors.invalidCredentials')}
 catch{error.value=t('login.errors.unexpected')}finally{isLoading.value=false}
}
</script>

<template>
  <div class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#191919] px-4">
    <div aria-hidden="true" class="absolute inset-0">
      <div class="absolute -left-24 -top-24 h-96 w-96 rounded-full bg-primary/20 blur-[120px]"></div>
      <div class="absolute -bottom-32 -right-16 h-96 w-96 rounded-full bg-primary/10 blur-[130px]"></div>
      <div class="absolute inset-0 opacity-[.035]" style="background-image:linear-gradient(rgba(255,255,255,.5) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.5) 1px,transparent 1px);background-size:32px 32px"></div>
    </div>
    <div class="absolute right-6 top-6 z-20 text-white"><LocaleToggle /></div>
    <div class="relative z-10 grid w-full max-w-4xl overflow-hidden rounded-[28px] border border-white/10 bg-[#222] shadow-2xl md:grid-cols-[1.05fr_.95fr]">
      <section class="relative hidden min-h-[560px] flex-col justify-between overflow-hidden bg-primary p-10 text-[#222] md:flex">
        <img :src="BrandIcon" alt="" class="h-20 w-20 rounded-2xl shadow-xl" />
        <div><p class="mb-3 text-xs font-black tracking-[.28em]">SMART MONITOR</p><h1 class="text-4xl font-black leading-tight">发现机会，<br/>让监控更简单。</h1><p class="mt-5 max-w-xs text-sm font-semibold leading-6 text-black/60">本地桌面运行 · 任务实时管理 · 数据智能分析</p></div>
        <p class="text-xs font-bold text-black/45">SBS 闲鱼助手 DESKTOP</p>
      </section>
      <Card class="flex min-h-[560px] flex-col justify-center rounded-none border-0 bg-[#222] px-5 text-white shadow-none sm:px-10">
        <div class="mb-8 md:hidden"><img :src="BrandIcon" alt="" class="mx-auto h-16 w-16 rounded-2xl" /></div>
        <div class="mb-8"><p class="mb-2 text-xs font-black tracking-[.22em] text-primary">WELCOME BACK</p><h2 class="text-3xl font-black">登录 SBS闲鱼助手</h2><p class="mt-2 text-sm text-white/45">{{ t('login.description') }}</p></div>
        <form @submit.prevent="handleLogin">
          <CardContent class="grid gap-5 p-0">
            <div class="grid gap-2"><Label for="username" class="text-white/70">{{ t('login.username') }}</Label><Input id="username" v-model="username" type="text" placeholder="admin" required class="h-12 border-white/10 bg-white/[.06] text-white placeholder:text-white/25 focus-visible:ring-primary" /></div>
            <div class="grid gap-2"><Label for="password" class="text-white/70">{{ t('login.password') }}</Label><Input id="password" v-model="password" type="password" required class="h-12 border-white/10 bg-white/[.06] text-white focus-visible:ring-primary" /></div>
            <div v-if="error" class="rounded-xl border border-red-400/20 bg-red-400/10 px-3 py-2 text-sm font-medium text-red-300" role="alert">{{ error }}</div>
          </CardContent>
          <CardFooter class="mt-7 p-0"><Button class="h-12 w-full rounded-xl font-black text-[#222] shadow-lg shadow-primary/15 hover:bg-amber-400" type="submit" :disabled="isLoading">{{ isLoading?t('login.submitting'):t('login.submit') }}</Button></CardFooter>
        </form>
      </Card>
    </div>
  </div>
</template>
