<script>
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	import relativeTime from 'dayjs/plugin/relativeTime';

	import { getChatLogs, deleteChatLogs } from '$lib/apis/chat-logs';

	import Pagination from '$lib/components/common/Pagination.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Download from '$lib/components/icons/Download.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';

	dayjs.extend(localizedFormat);
	dayjs.extend(relativeTime);

	const i18n = getContext('i18n');

	let page = 1;
	let chatLogs = null;
	let total = null;
	let loading = false;

	// Filters
	let userId = '';
	let model = '';
	let startDate = '';
	let endDate = '';

	// Export
	let exportLoading = false;

	const getChatLogsList = async () => {
		loading = true;
		
		try {
			const filter = {
				limit: 50,
				skip: (page - 1) * 50
			};

			// Add filters if they exist
			if (userId) filter.user_id = userId;
			if (model) filter.model = model;
			if (startDate) filter.start_date = startDate;
			if (endDate) filter.end_date = endDate;

			const res = await getChatLogs(localStorage.token, filter, true); // true for admin endpoint
			
			if (res) {
				chatLogs = res.data;
				total = res.count;
			}
		} catch (error) {
			console.error('Error fetching chat logs:', error);
			toast.error(`${error}`);
		} finally {
			loading = false;
		}
	};

	const handleFilterChange = () => {
		page = 1;
		getChatLogsList();
	};

	const clearFilters = () => {
		userId = '';
		model = '';
		startDate = '';
		endDate = '';
		page = 1;
		getChatLogsList();
	};

	const exportChatLogs = async () => {
		exportLoading = true;
		
		try {
			// In a real implementation, this would call an export API
			// For now, we'll simulate the export by downloading the current data
			const dataStr = JSON.stringify(chatLogs, null, 2);
			const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
			
			const exportFileDefaultName = `chat-logs-${new Date().toISOString().slice(0, 10)}.json`;
			
			const linkElement = document.createElement('a');
			linkElement.setAttribute('href', dataUri);
			linkElement.setAttribute('download', exportFileDefaultName);
			linkElement.click();
			
			toast.success($i18n.t('Chat logs exported successfully'));
		} catch (error) {
			console.error('Error exporting chat logs:', error);
			toast.error($i18n.t('Failed to export chat logs'));
		} finally {
			exportLoading = false;
		}
	};

	const deleteAllChatLogs = async () => {
		if (!confirm($i18n.t('Are you sure you want to delete all chat logs? This action cannot be undone.'))) {
			return;
		}

		try {
			const filter = {};
			
			// Add filters if they exist
			if (userId) filter.user_id = userId;
			if (model) filter.model = model;
			if (startDate) filter.start_date = startDate;
			if (endDate) filter.end_date = endDate;

			const res = await deleteChatLogs(localStorage.token, filter, true); // true for admin endpoint
			
			if (res) {
				toast.success($i18n.t('All chat logs deleted successfully'));
				page = 1;
				getChatLogsList();
			}
		} catch (error) {
			console.error('Error deleting chat logs:', error);
			toast.error($i18n.t('Failed to delete chat logs'));
		}
	};

	$: if (page) {
		getChatLogsList();
	}

	onMount(() => {
		getChatLogsList();
	});
</script>

<div class="flex flex-col h-full w-full">
	<!-- Filters -->
	<div class="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
					{$i18n.t('User ID')}
				</label>
				<input
					type="text"
					class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
					bind:value={userId}
					on:input={handleFilterChange}
					placeholder={$i18n.t('Filter by user ID')}
				/>
			</div>
			
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
					{$i18n.t('Model')}
				</label>
				<input
					type="text"
					class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
					bind:value={model}
					on:input={handleFilterChange}
					placeholder={$i18n.t('Filter by model')}
				/>
			</div>
			
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
					{$i18n.t('Start Date')}
				</label>
				<input
					type="date"
					class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
					bind:value={startDate}
					on:change={handleFilterChange}
				/>
			</div>
			
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
					{$i18n.t('End Date')}
				</label>
				<input
					type="date"
					class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
					bind:value={endDate}
					on:change={handleFilterChange}
				/>
			</div>
		</div>
		
		<div class="flex justify-end mt-4 space-x-2">
			<button
				class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
				on:click={clearFilters}
			>
				{$i18n.t('Clear Filters')}
			</button>
			
			<Tooltip content={$i18n.t('Export Chat Logs')}>
				<button
					class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
					disabled={exportLoading}
					on:click={exportChatLogs}
				>
					{#if exportLoading}
						<Spinner className="size-4" />
					{:else}
						<div class="flex items-center">
							<Download className="size-4 mr-1" />
							{$i18n.t('Export')}
						</div>
					{/if}
				</button>
			</Tooltip>
			
			<Tooltip content={$i18n.t('Delete All Chat Logs')}>
				<button
					class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
					on:click={deleteAllChatLogs}
				>
					<div class="flex items-center">
						<GarbageBin className="size-4 mr-1" />
						{$i18n.t('Delete All')}
					</div>
				</button>
			</Tooltip>
		</div>
	</div>

	<!-- Chat Logs Table -->
	<div class="flex-1 overflow-auto">
		{#if loading}
			<div class="flex justify-center items-center h-64">
				<Spinner className="size-8" />
			</div>
		{:else if chatLogs === null}
			<div class="text-center py-10 text-gray-500">
				{$i18n.t('No chat logs found')}
			</div>
		{:else if chatLogs.length === 0}
			<div class="text-center py-10 text-gray-500">
				{$i18n.t('No chat logs found with current filters')}
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
					<thead class="bg-gray-50 dark:bg-gray-800">
						<tr>
							<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$i18n.t('Title')}
							</th>
							<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$i18n.t('User')}
							</th>
							<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$i18n.t('Model')}
							</th>
							<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$i18n.t('Count')}
							</th>
							<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$i18n.t('Created At')}
							</th>
							<th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$i18n.t('Actions')}
							</th>
						</tr>
					</thead>
					<tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
						{#each chatLogs as log}
							<tr class="hover:bg-gray-50 dark:hover:bg-gray-800">
								<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
									{log.title || 'Untitled'}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{log.user_name}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{log.model}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{log.messages.length}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
									{dayjs(log.created_at * 1000).format('LLL')}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
									<button
										class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
										on:click={() => {
											// View log details
											console.log('View log:', log);
										}}
									>
										{$i18n.t('View')}
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>

	<!-- Pagination -->
	{#if total && total > 50}
		<div class="mt-6">
			<Pagination bind:page count={total} perPage={50} />
		</div>
	{/if}
</div>
