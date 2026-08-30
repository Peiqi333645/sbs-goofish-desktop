<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { listAccounts, getAccount, createAccount, updateAccount, deleteAccount, startQrLogin, getQrLoginStatus, cancelQrLogin, type AccountItem } from '@/api/accounts'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { toast } from '@/components/ui/toast'
const { t } = useI18n()

const accounts = ref<AccountItem[]>([])
const isLoading = ref(false)
const isSaving = ref(false)
const router = useRouter()

const isCreateDialogOpen = ref(false)
const isQrDialogOpen = ref(false)
const qrName = ref('')
const qrSessionId = ref('')
const qrStatus = ref('idle')
const qrMessage = ref('点击下方按钮后，将打开闲鱼官方扫码登录页面。')
const isEditDialogOpen = ref(false)
const isDeleteDialogOpen = ref(false)

const newName = ref('')
const newContent = ref('')
const editName = ref('')
const editContent = ref('')
const deleteName = ref('')

async function fetchAccounts() {
  isLoading.value = true
  try {
    accounts.value = await listAccounts()
  } catch (e) {
    toast({ title: t('accounts.toasts.loadFailed'), description: (e as Error).message, variant: 'destructive' })
  } finally {
    isLoading.value = false
  }
}

function openQrDialog() {
  qrName.value = ''
  qrSessionId.value = ''
  qrStatus.value = 'idle'
  qrMessage.value = '点击“打开扫码页面”后，使用手机淘宝扫码并在手机上确认。'
  isQrDialogOpen.value = true
}

async function handleQrLogin() {
  if (!qrName.value.trim()) {
    toast({ title: '请先填写账号名称', variant: 'destructive' })
    return
  }
  isSaving.value = true
  try {
    const session = await startQrLogin(qrName.value.trim())
    qrSessionId.value = session.session_id
    qrStatus.value = session.status
    qrMessage.value = session.message
    while (isQrDialogOpen.value && !['success', 'error', 'cancelled'].includes(qrStatus.value)) {
      await new Promise(resolve => setTimeout(resolve, 1500))
      const current = await getQrLoginStatus(session.session_id)
      qrStatus.value = current.status
      qrMessage.value = current.message
    }
    if (qrStatus.value === 'success') {
      toast({ title: '扫码登录成功' })
      isQrDialogOpen.value = false
      await fetchAccounts()
    }
  } catch (e) {
    qrStatus.value = 'error'
    qrMessage.value = (e as Error).message
    toast({ title: '扫码登录失败', description: qrMessage.value, variant: 'destructive' })
  } finally {
    isSaving.value = false
  }
}

async function closeQrDialog() {
  if (qrSessionId.value && !['success', 'error', 'cancelled'].includes(qrStatus.value)) {
    await cancelQrLogin(qrSessionId.value).catch(() => undefined)
  }
  isQrDialogOpen.value = false
}

function openCreateDialog() {
  newName.value = ''
  newContent.value = ''
  isCreateDialogOpen.value = true
}

async function openEditDialog(name: string) {
  isSaving.value = true
  try {
    const detail = await getAccount(name)
    editName.value = detail.name
    editContent.value = detail.content
    isEditDialogOpen.value = true
  } catch (e) {
    toast({ title: t('accounts.toasts.loadContentFailed'), description: (e as Error).message, variant: 'destructive' })
  } finally {
    isSaving.value = false
  }
}

function openDeleteDialog(name: string) {
  deleteName.value = name
  isDeleteDialogOpen.value = true
}

function goCreateTask(name: string) {
  router.push({ path: '/tasks', query: { account: name, create: '1' } })
}

async function handleCreateAccount() {
  if (!newName.value.trim() || !newContent.value.trim()) {
    toast({ title: t('accounts.toasts.incomplete'), description: t('accounts.toasts.createDescriptionRequired'), variant: 'destructive' })
    return
  }
  isSaving.value = true
  try {
    await createAccount({ name: newName.value.trim(), content: newContent.value.trim() })
    toast({ title: t('accounts.toasts.created') })
    isCreateDialogOpen.value = false
    await fetchAccounts()
  } catch (e) {
    toast({ title: t('accounts.toasts.createFailed'), description: (e as Error).message, variant: 'destructive' })
  } finally {
    isSaving.value = false
  }
}

async function handleUpdateAccount() {
  if (!editContent.value.trim()) {
    toast({ title: t('accounts.toasts.contentRequired'), description: t('accounts.toasts.updateDescriptionRequired'), variant: 'destructive' })
    return
  }
  isSaving.value = true
  try {
    await updateAccount(editName.value, editContent.value.trim())
    toast({ title: t('accounts.toasts.updated') })
    isEditDialogOpen.value = false
    await fetchAccounts()
  } catch (e) {
    toast({ title: t('accounts.toasts.updateFailed'), description: (e as Error).message, variant: 'destructive' })
  } finally {
    isSaving.value = false
  }
}

async function handleDeleteAccount() {
  isSaving.value = true
  try {
    await deleteAccount(deleteName.value)
    toast({ title: t('accounts.toasts.deleted') })
    isDeleteDialogOpen.value = false
    await fetchAccounts()
  } catch (e) {
    toast({ title: t('accounts.toasts.deleteFailed'), description: (e as Error).message, variant: 'destructive' })
  } finally {
    isSaving.value = false
  }
}

onMounted(fetchAccounts)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">{{ t('accounts.title') }}</h1>
        <p class="text-sm text-gray-500 mt-1">{{ t('accounts.description') }}</p>
      </div>
      <Button class="w-full sm:w-auto" @click="openQrDialog">+ 扫码登录闲鱼账号</Button>
    </div>

    <Card class="app-surface mb-6 border-none">
      <CardHeader>
        <CardTitle>推荐使用扫码登录</CardTitle>
      </CardHeader>
      <CardContent class="space-y-3 text-sm text-gray-600">
        <p>软件只会打开闲鱼官方登录页面。请使用手机淘宝扫码并确认，登录状态保存在当前电脑，不需要复制 Cookie 或 JSON。</p>
        <div class="flex flex-wrap gap-2">
          <Button @click="openQrDialog">打开扫码登录</Button>
          <Button variant="outline" @click="openCreateDialog">高级方式：导入 JSON</Button>
        </div>
        <p class="text-xs text-muted-foreground">请勿把 JSON 登录状态发送给他人；它可能包含可直接代表账号登录的 Cookie。</p>
      </CardContent>
    </Card>

    <Card class="app-surface border-none">
      <CardHeader>
        <CardTitle>{{ t('accounts.list.title') }}</CardTitle>
        <CardDescription>{{ t('accounts.list.description') }}</CardDescription>
      </CardHeader>
      <CardContent>
        <div class="space-y-4 md:hidden">
          <div v-if="isLoading" class="py-10 text-center text-sm text-muted-foreground">{{ t('common.loading') }}</div>
          <div v-else-if="accounts.length === 0" class="py-10 text-center text-sm text-muted-foreground">{{ t('accounts.list.empty') }}</div>
          <article
            v-else
            v-for="account in accounts"
            :key="account.name"
            class="app-surface-subtle p-4"
          >
            <div class="space-y-2">
              <div class="flex items-center justify-between gap-3">
                <h3 class="truncate text-base font-semibold text-slate-900">{{ account.name }}</h3>
                <Button size="sm" variant="outline" @click="goCreateTask(account.name)">{{ t('accounts.list.createTask') }}</Button>
              </div>
              <p class="break-all text-sm text-slate-500">{{ account.path }}</p>
            </div>
            <div class="mt-4 flex flex-wrap gap-2">
              <Button size="sm" variant="outline" class="flex-1 min-w-[120px]" @click="openEditDialog(account.name)">{{ t('accounts.list.update') }}</Button>
              <Button size="sm" variant="destructive" class="flex-1 min-w-[120px]" @click="openDeleteDialog(account.name)">{{ t('accounts.list.delete') }}</Button>
            </div>
          </article>
        </div>

        <div class="hidden md:block">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{{ t('accounts.list.name') }}</TableHead>
                <TableHead>{{ t('accounts.list.file') }}</TableHead>
                <TableHead class="text-right">{{ t('accounts.list.actions') }}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="isLoading">
                <TableCell colspan="3" class="h-20 text-center text-muted-foreground">{{ t('common.loading') }}</TableCell>
              </TableRow>
              <TableRow v-else-if="accounts.length === 0">
                <TableCell colspan="3" class="h-20 text-center text-muted-foreground">{{ t('accounts.list.empty') }}</TableCell>
              </TableRow>
              <TableRow v-else v-for="account in accounts" :key="account.name">
                <TableCell class="font-medium">{{ account.name }}</TableCell>
                <TableCell class="text-sm text-gray-500">{{ account.path }}</TableCell>
                <TableCell class="text-right">
                  <div class="flex justify-end gap-2">
                    <Button size="sm" variant="outline" @click="goCreateTask(account.name)">{{ t('accounts.list.createTask') }}</Button>
                    <Button size="sm" variant="outline" @click="openEditDialog(account.name)">{{ t('accounts.list.update') }}</Button>
                    <Button size="sm" variant="destructive" @click="openDeleteDialog(account.name)">{{ t('accounts.list.delete') }}</Button>
                  </div>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <Dialog v-model:open="isQrDialogOpen">
      <DialogContent class="sm:max-w-[520px]">
        <DialogHeader>
          <DialogTitle>扫码登录闲鱼账号</DialogTitle>
          <DialogDescription>二维码来自闲鱼官方页面，扫码后请在手机淘宝中确认。</DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div class="grid gap-2">
            <Label>账号名称</Label>
            <Input v-model="qrName" :disabled="qrStatus !== 'idle'" placeholder="例如：我的闲鱼账号" />
          </div>
          <div class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
            {{ qrMessage }}
          </div>
          <p v-if="qrStatus === 'waiting'" class="text-xs text-muted-foreground">浏览器登录窗口会自动关闭；请不要在扫码完成前手动关闭。</p>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="closeQrDialog">取消</Button>
          <Button v-if="qrStatus === 'idle' || qrStatus === 'error' || qrStatus === 'cancelled'" :disabled="isSaving" @click="handleQrLogin">
            {{ isSaving ? '正在打开…' : '打开扫码页面' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <Dialog v-model:open="isCreateDialogOpen">
      <DialogContent class="sm:max-w-[700px]">
        <DialogHeader>
          <DialogTitle>高级方式：导入 JSON 登录状态</DialogTitle>
          <DialogDescription>仅用于扫码登录不可用时。JSON 内可能包含敏感 Cookie，请勿分享给任何人。</DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div class="grid gap-2">
            <Label>{{ t('accounts.createDialog.name') }}</Label>
            <Input v-model="newName" :placeholder="t('accounts.createDialog.namePlaceholder')" />
          </div>
          <div class="grid gap-2">
            <Label>{{ t('accounts.createDialog.jsonContent') }}</Label>
            <Textarea v-model="newContent" class="min-h-[200px]" :placeholder="t('accounts.createDialog.jsonPlaceholder')" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="isCreateDialogOpen = false">{{ t('common.cancel') }}</Button>
          <Button :disabled="isSaving" @click="handleCreateAccount">
            {{ isSaving ? t('common.saving') : t('common.save') }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <Dialog v-model:open="isEditDialogOpen">
      <DialogContent class="sm:max-w-[700px]">
        <DialogHeader>
          <DialogTitle>{{ t('accounts.editDialog.title', { name: editName }) }}</DialogTitle>
          <DialogDescription>{{ t('accounts.editDialog.description') }}</DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div class="grid gap-2">
            <Label>{{ t('accounts.createDialog.jsonContent') }}</Label>
            <Textarea v-model="editContent" class="min-h-[200px]" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="isEditDialogOpen = false">{{ t('common.cancel') }}</Button>
          <Button :disabled="isSaving" @click="handleUpdateAccount">
            {{ isSaving ? t('common.saving') : t('common.save') }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <Dialog v-model:open="isDeleteDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ t('accounts.deleteDialog.title') }}</DialogTitle>
          <DialogDescription>{{ t('accounts.deleteDialog.description', { name: deleteName }) }}</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" @click="isDeleteDialogOpen = false">{{ t('common.cancel') }}</Button>
          <Button variant="destructive" :disabled="isSaving" @click="handleDeleteAccount">
            {{ isSaving ? t('accounts.deleteDialog.deleting') : t('accounts.list.delete') }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
