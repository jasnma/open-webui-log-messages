<script>
	import { page } from '$app/stores';
	import { onMount, getContext } from 'svelte';
	import { user } from '$lib/stores';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';

	import { getChatLogs } from '$lib/apis/chat-logs';

	const i18n = getContext('i18n');

	let chatLog = null;
	let loading = true;

	onMount(async () => {
		if ($user?.role !== 'admin') {
			await goto('/');
			return;
		}

		const conversationId = $page.params.id;
		if (!conversationId) {
			toast.error($i18n.t('Invalid chat log ID'));
			await goto('/admin/chat-logs');
			return;
		}

		try {
			loading = true;
			// Fetch chat log by conversation_id
			const response = await getChatLogs(localStorage.token, { conversation_id: conversationId }, true);
			if (response && response.data && response.data.length > 0) {
				chatLog = response.data[0];
			} else {
				toast.error($i18n.t('Chat log not found'));
				await goto('/admin/chat-logs');
			}
		} catch (error) {
			console.error('Error fetching chat log:', error);
			toast.error($i18n.t('Failed to load chat log'));
			await goto('/admin/chat-logs');
		} finally {
			loading = false;
		}
	});
</script>

<div class="flex flex-col h-full w-full p-4">
	<div class="flex justify-between items-center mb-4">
		<h1 class="text-2xl font-bold text-gray-800 dark:text-gray-200">
			{chatLog?.title || 'Untitled'}
		</h1>
		<button
			class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
			on:click={() => {
				goto('/admin/chat-logs');
			}}
		>
			{$i18n.t('Back to Logs')}
		</button>
	</div>

	{#if loading}
		<div class="flex justify-center items-center h-64">
			<div class="text-center">
				<div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
				<p class="mt-2 text-gray-600 dark:text-gray-300">{$i18n.t('Loading chat log...')}</p>
			</div>
		</div>
	{:else if chatLog}
		<div class="flex flex-wrap gap-4 mb-1">
			<div class="flex-1 min-w-[200px]">
				<span class="text-sm font-medium text-gray-500 dark:text-gray-400">{$i18n.t('User')}</span>
				<p class="mt-1 text-sm text-gray-900 dark:text-white">{chatLog.user_name}</p>
			</div>
			<div class="flex-1 min-w-[200px]">
				<span class="text-sm font-medium text-gray-500 dark:text-gray-400">{$i18n.t('Model')}</span>
				<p class="mt-1 text-sm text-gray-900 dark:text-white">{chatLog.model}</p>
			</div>
			<div class="flex-1 min-w-[200px]">
				<span class="text-sm font-medium text-gray-500 dark:text-gray-400">{$i18n.t('Created At')}</span>
				<p class="mt-1 text-sm text-gray-900 dark:text-white">
					{new Date(chatLog.created_at * 1000).toLocaleString()}
				</p>
			</div>
		</div>

		<div class="bg-white dark:bg-gray-800 rounded-lg shadow">
			<div><div class="mt-2 bg-gray-50 dark:bg-gray-700 rounded-lg p-4 overflow-y-auto">
					{#each chatLog.messages as message, index}
						{#if message.role !== 'system'}
							<div class="mb-4 last:mb-0">
								<div class="flex items-start">
									<span class="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 text-xs font-medium mr-2 flex-shrink-0">
										{index + 1}
									</span>
									<div class="flex-1">
										<div class="flex items-center mb-1">
											<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-{message.role === 'user' ? 'green' : 'purple'}-100 text-{message.role === 'user' ? 'green' : 'purple'}-800 mr-2">
												{message.role}
											</span>
											{#if message.model}
												<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
													{message.model}
												</span>
											{/if}
										</div>
										{#if typeof message.content === 'string'}
											<pre class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words">{message.content}</pre>
										{:else}
											<pre class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words">{JSON.stringify(message.content, null, 2)}</pre>
										{/if}
									</div>
								</div>
							</div>
						{/if}
					{/each}
					{#if chatLog.response}
						<div class="mb-4 last:mb-0">
							<div class="flex items-start">
								<span class="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 text-xs font-medium mr-2 flex-shrink-0">
									{chatLog.messages.length + 1}
								</span>
								<div class="flex-1">
									<div class="flex items-center mb-1">
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 mr-2">
											assistant
										</span>
									</div>
									{#if typeof chatLog.response === 'string'}
										<pre class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words">{chatLog.response}</pre>
									{:else}
										<pre class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words">{JSON.stringify(chatLog.response, null, 2)}</pre>
									{/if}
								</div>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	{:else}
		<div class="text-center py-10 text-gray-500">
			{$i18n.t('No chat log found')}
		</div>
	{/if}
</div>
