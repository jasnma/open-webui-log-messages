<script>
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { toast } from 'svelte-sonner';

	import ChatLogsList from '$lib/components/admin/ChatLogsList.svelte';

	const i18n = getContext('i18n');

	onMount(async () => {
		if ($user?.role !== 'admin') {
			await goto('/');
		}
	});
</script>

<div class="flex flex-col h-full w-full p-4">
	<div class="flex justify-between items-center mb-6">
		<h1 class="text-2xl font-bold text-gray-800 dark:text-gray-200">
			{$i18n.t('Chat Logs')}
		</h1>
	</div>

	<ChatLogsList />
</div>
