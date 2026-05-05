<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Navbar from '$lib/widgets/Navbar.svelte';
	import Sidebar from '$lib/widgets/Sidebar.svelte';
	import { API_BASE_URL } from '$lib/config';
	import { 
		ScrollText,
		Search,
		Filter,
		RefreshCw,
		Download,
		AlertCircle,
		CheckCircle,
		XCircle,
		User,
		Calendar,
		Activity,
		ChevronLeft,
		ChevronRight
	} from 'lucide-svelte';

	let sidebarExpanded = false;
	let currentUser: any | null = null;
	let loading = true;
	
	function toggleSidebar() {
		sidebarExpanded = !sidebarExpanded;
	}
	
	// Filter states
	let searchQuery = '';
	let actionFilter = '';
	let userFilter = '';
	
	// Pagination
	let currentPage = 1;
	let itemsPerPage = 50;
	let totalCount = 0;
	
	// Data
	interface AuditLog {
		log_id: number;
		user_id: number | null;
		user_name: string | null;
		user_email: string | null;
		action: string;
		details: string;
		timestamp: string;
	}
	
	let logs: AuditLog[] = [];
	let actionStats: Array<{ action: string; count: number }> = [];
	
	// Action type colors
	const actionColors: Record<string, string> = {
		'LOGIN': '#10B981',
		'LOGIN_FAILED': '#EF4444',
		'REGISTER': '#3B82F6',
		'UPDATE_USER_STATUS': '#F59E0B',
		'UPDATE_USER_ROLE': '#8B5CF6',
		'DELETE_USER': '#EF4444',
		'SELECT_DASHBOARD_STATS': '#6B7280',
		'VIEW_AUDIT_LOGS': '#EC4899'
	};
	
	function getActionColor(action: string): string {
		return actionColors[action] || '#6B7280';
	}
	
	function getActionIcon(action: string) {
		if (action.includes('DELETE') || action.includes('FAILED')) return XCircle;
		if (action.includes('LOGIN') || action.includes('REGISTER')) return CheckCircle;
		return Activity;
	}

	onMount(() => {
		// Check if user is logged in and is admin
		const userData = sessionStorage.getItem('user');
		if (userData) {
			try {
				const parsedUser = JSON.parse(userData);
				currentUser = parsedUser;
				
				// Check if user is admin
				if (currentUser.role !== 'admin') {
					alert('Access denied. Admin privileges required.');
					goto('/home');
					return;
				}
				
				fetchAuditLogs();
			} catch (e) {
				console.error('Failed to parse user data:', e);
				goto('/');
			}
		} else {
			goto('/');
		}
	});

	async function fetchAuditLogs() {
		if (!currentUser || !currentUser.user_id) return;
		
		loading = true;
		try {
			const offset = (currentPage - 1) * itemsPerPage;
			let url = `${API_BASE_URL}/admin/audit-logs?admin_id=${currentUser.user_id}&limit=${itemsPerPage}&offset=${offset}`;
			
			if (actionFilter) url += `&action_filter=${actionFilter}`;
			if (userFilter) url += `&user_filter=${userFilter}`;
			
			const response = await fetch(url);
			const data = await response.json();
			
			if (data.success) {
				logs = data.logs;
				actionStats = data.action_stats;
				totalCount = data.total_count;
			}
		} catch (error) {
			console.error('Error fetching audit logs:', error);
		} finally {
			loading = false;
		}
	}
	
	// Reactive: Re-fetch when filters change
	$: if (currentUser && (actionFilter || userFilter)) {
		currentPage = 1; // Reset to first page when filters change
		fetchAuditLogs();
	}
	
	// Filter logs based on search query (client-side)
	$: filteredLogs = logs.filter(log => {
		if (!searchQuery) return true;
		
		const query = searchQuery.toLowerCase();
		return (
			log.action.toLowerCase().includes(query) ||
			log.details.toLowerCase().includes(query) ||
			(log.user_name && log.user_name.toLowerCase().includes(query)) ||
			(log.user_email && log.user_email.toLowerCase().includes(query))
		);
	});
	
	// Pagination
	$: totalPages = Math.ceil(totalCount / itemsPerPage);
	
	function nextPage() {
		if (currentPage < totalPages) {
			currentPage++;
			fetchAuditLogs();
		}
	}
	
	function prevPage() {
		if (currentPage > 1) {
			currentPage--;
			fetchAuditLogs();
		}
	}
	
	function refreshLogs() {
		currentPage = 1;
		fetchAuditLogs();
	}
	
	function formatTimestamp(timestamp: string): string {
		const date = new Date(timestamp);
		return date.toLocaleString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		});
	}
</script>

<svelte:head>
	<title>Audit Logs - CarbonTrack</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Top Navigation -->
	<Navbar {toggleSidebar} />

	<!-- Sidebar -->
	<Sidebar {sidebarExpanded} currentPage="audit-logs" />

	<!-- Main Content -->
	<div class="lg:ml-64 pt-16">
		<div class="p-6 space-y-6">
			<!-- Header Section -->
			<div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
				<div>
					<h1 class="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
						<ScrollText class="w-8 h-8 text-purple-600" />
						Audit Logs
					</h1>
					<p class="text-gray-600">Monitor all system activities and user actions</p>
				</div>
				
				<button 
					on:click={refreshLogs}
					class="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
				>
					<RefreshCw class="w-5 h-5" />
					Refresh
				</button>
			</div>

			<!-- Statistics Cards -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-6">
				<div class="bg-white border border-gray-200 rounded-xl p-6">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-500 text-sm">Total Logs</p>
							<p class="text-3xl font-bold text-gray-900">{totalCount.toLocaleString()}</p>
						</div>
						<div class="p-3 bg-purple-50 rounded-lg">
							<ScrollText class="w-6 h-6 text-purple-600" />
						</div>
					</div>
				</div>

				<div class="bg-white border border-gray-200 rounded-xl p-6">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-500 text-sm">Action Types</p>
							<p class="text-3xl font-bold text-gray-900">{actionStats.length}</p>
						</div>
						<div class="p-3 bg-blue-50 rounded-lg">
							<Activity class="w-6 h-6 text-blue-600" />
						</div>
					</div>
				</div>

				<div class="bg-white border border-gray-200 rounded-xl p-6">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-500 text-sm">Current Page</p>
							<p class="text-3xl font-bold text-gray-900">{currentPage} / {totalPages}</p>
						</div>
						<div class="p-3 bg-green-50 rounded-lg">
							<Calendar class="w-6 h-6 text-green-600" />
						</div>
					</div>
				</div>

				<div class="bg-white border border-gray-200 rounded-xl p-6">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-500 text-sm">Showing</p>
							<p class="text-3xl font-bold text-gray-900">{logs.length}</p>
						</div>
						<div class="p-3 bg-orange-50 rounded-lg">
							<Filter class="w-6 h-6 text-orange-600" />
						</div>
					</div>
				</div>
			</div>

			<!-- Action Statistics -->
			{#if actionStats.length > 0}
				<div class="bg-white border border-gray-200 rounded-xl p-6">
					<h3 class="text-xl font-semibold text-gray-900 mb-4">Action Statistics</h3>
					<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
						{#each actionStats as stat}
							<div class="flex flex-col items-center p-3 bg-gray-50 rounded-lg">
								<div 
									class="w-12 h-12 rounded-full flex items-center justify-center mb-2"
									style="background-color: {getActionColor(stat.action)}20"
								>
									<svelte:component 
										this={getActionIcon(stat.action)} 
										class="w-6 h-6" 
										style="color: {getActionColor(stat.action)}"
									/>
								</div>
								<p class="text-xs text-gray-600 text-center truncate w-full">{stat.action}</p>
								<p class="text-lg font-bold text-gray-900">{stat.count}</p>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Filters and Search -->
			<div class="bg-white border border-gray-200 rounded-xl p-6">
				<div class="flex flex-col lg:flex-row gap-4">
					<!-- Search -->
					<div class="flex-1 relative">
						<Search class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
						<input 
							type="text" 
							placeholder="Search logs by action, details, user..."
							bind:value={searchQuery}
							class="w-full bg-gray-50 border border-gray-300 text-gray-900 pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
						/>
					</div>
					
					<!-- Action Filter -->
					<select 
						bind:value={actionFilter}
						class="bg-gray-50 border border-gray-300 text-gray-900 px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
					>
						<option value="">All Actions</option>
						{#each actionStats as stat}
							<option value={stat.action}>{stat.action} ({stat.count})</option>
						{/each}
					</select>
				</div>
			</div>

			<!-- Logs Table -->
			<div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
				<div class="overflow-x-auto">
					{#if loading}
						<div class="h-64 flex items-center justify-center">
							<RefreshCw class="w-8 h-8 text-gray-400 animate-spin" />
						</div>
					{:else if filteredLogs.length > 0}
						<table class="w-full">
							<thead class="bg-gray-50 border-b border-gray-200">
								<tr>
									<th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
									<th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
									<th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">User</th>
									<th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
									<th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-200">
								{#each filteredLogs as log}
									<tr class="hover:bg-gray-50 transition-colors">
										<td class="px-6 py-4 text-sm text-gray-500">
											#{log.log_id}
										</td>
										<td class="px-6 py-4 text-sm text-gray-600 whitespace-nowrap">
											<div class="flex items-center gap-2">
												<Calendar class="w-4 h-4 text-gray-400" />
												{formatTimestamp(log.timestamp)}
											</div>
										</td>
										<td class="px-6 py-4 text-sm">
											{#if log.user_name}
												<div class="flex items-center gap-2">
													<div class="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
														<User class="w-4 h-4 text-purple-600" />
													</div>
													<div>
														<p class="text-gray-900 font-medium">{log.user_name}</p>
														<p class="text-gray-500 text-xs">{log.user_email}</p>
													</div>
												</div>
											{:else}
												<span class="text-gray-400 italic">System</span>
											{/if}
										</td>
										<td class="px-6 py-4 text-sm">
											<span 
												class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium"
												style="background-color: {getActionColor(log.action)}20; color: {getActionColor(log.action)}"
											>
												<svelte:component this={getActionIcon(log.action)} class="w-3 h-3" />
												{log.action}
											</span>
										</td>
										<td class="px-6 py-4 text-sm text-gray-600">
											<div class="max-w-md truncate" title={log.details}>
												{log.details}
											</div>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					{:else}
						<div class="h-64 flex items-center justify-center">
							<div class="text-center">
								<AlertCircle class="w-12 h-12 text-gray-300 mx-auto mb-2" />
								<p class="text-sm text-gray-500">No audit logs found</p>
								<p class="text-xs text-gray-400 mt-1">Try adjusting your filters</p>
							</div>
						</div>
					{/if}
				</div>

				<!-- Pagination -->
				{#if !loading && totalPages > 1}
					<div class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
						<p class="text-sm text-gray-600">
							Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, totalCount)} of {totalCount} logs
						</p>
						<div class="flex items-center gap-2">
							<button 
								on:click={prevPage}
								disabled={currentPage === 1}
								class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
							>
								<ChevronLeft class="w-5 h-5" />
							</button>
							<span class="text-sm text-gray-600">
								Page {currentPage} of {totalPages}
							</span>
							<button 
								on:click={nextPage}
								disabled={currentPage === totalPages}
								class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
							>
								<ChevronRight class="w-5 h-5" />
							</button>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	/* Custom scrollbar styling */
	:global(::-webkit-scrollbar) {
		width: 8px;
		height: 8px;
	}

	:global(::-webkit-scrollbar-track) {
		background: #f3f4f6;
		border-radius: 4px;
	}

	:global(::-webkit-scrollbar-thumb) {
		background: #d1d5db;
		border-radius: 4px;
	}

	:global(::-webkit-scrollbar-thumb:hover) {
		background: #9ca3af;
	}
</style>
