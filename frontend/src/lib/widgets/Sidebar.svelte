<script lang="ts">
	import { 
		BarChart3, 
		Factory, 
		Lightbulb, 
		Target, 
		Recycle, 
		FileText,
		Shield,
		ScrollText
	} from 'lucide-svelte';
	import { user, type User } from '../../stores';
	
	export let sidebarExpanded = true;
	export let currentPage = 'home';

	let currentUser: User | null = null;
	user.subscribe(value => {
		currentUser = value;
	});
</script>

<!-- Left Sidebar -->
<aside class="fixed left-0 top-16 h-full bg-white border-r border-gray-200 transition-all duration-300 z-40 {sidebarExpanded ? 'w-64' : 'w-16'} lg:w-64">
	<nav class="p-4 space-y-2">
		<a href="/home" class="flex items-center gap-3 px-3 py-2 rounded-lg {currentPage === 'home' ? 'bg-green-50 text-green-700' : 'text-gray-600'} hover:bg-green-50 hover:text-green-700 transition-colors">
			<BarChart3 class="w-5 h-5" />
			<span class="hidden lg:block {sidebarExpanded ? 'block' : 'hidden'}">Dashboard</span>
		</a>
		<a href="/emission-data" class="flex items-center gap-3 px-3 py-2 rounded-lg {currentPage === 'emission-data' ? 'bg-green-50 text-green-700' : 'text-gray-600'} hover:bg-green-50 hover:text-green-700 transition-colors">
			<Factory class="w-5 h-5" />
			<span class="hidden lg:block {sidebarExpanded ? 'block' : 'hidden'}">Emission Data</span>
		</a>
		<a href="/ai-insights" class="flex items-center gap-3 px-3 py-2 rounded-lg {currentPage === 'ai-insights' ? 'bg-green-50 text-green-700' : 'text-gray-600'} hover:bg-green-50 hover:text-green-700 transition-colors">
			<Lightbulb class="w-5 h-5" />
			<span class="hidden lg:block {sidebarExpanded ? 'block' : 'hidden'}">AI Insights</span>
		</a>
		<a href="/recommendations" class="flex items-center gap-3 px-3 py-2 rounded-lg {currentPage === 'recommendations' ? 'bg-green-50 text-green-700' : 'text-gray-600'} hover:bg-green-50 hover:text-green-700 transition-colors">
			<Target class="w-5 h-5" />
			<span class="hidden lg:block {sidebarExpanded ? 'block' : 'hidden'}">Recommendations</span>
		</a>
		<!-- <a href="/sustainability" class="flex items-center gap-3 px-3 py-2 rounded-lg {currentPage === 'sustainability' ? 'bg-green-50 text-green-700' : 'text-gray-600'} hover:bg-green-50 hover:text-green-700 transition-colors">
			<Recycle class="w-5 h-5" />
			<span class="hidden lg:block {sidebarExpanded ? 'block' : 'hidden'}">Sustainability</span>
		</a>
		<a href="/reports" class="flex items-center gap-3 px-3 py-2 rounded-lg {currentPage === 'reports' ? 'bg-green-50 text-green-700' : 'text-gray-600'} hover:bg-green-50 hover:text-green-700 transition-colors">
			<FileText class="w-5 h-5" />
			<span class="hidden lg:block {sidebarExpanded ? 'block' : 'hidden'}">Reports</span>
		</a> -->

		<!-- Admin Link (only visible to admins) -->
		{#if currentUser && currentUser.role === 'admin'}
			<a href="/admin" class="flex items-center gap-3 px-3 py-2 rounded-lg {currentPage === 'admin' ? 'bg-purple-50 text-purple-700' : 'text-gray-600'} hover:bg-purple-50 hover:text-purple-700 transition-colors border-t border-gray-200 mt-2 pt-4">
				<Shield class="w-5 h-5" />
				<span class="hidden lg:block {sidebarExpanded ? 'block' : 'hidden'}">Admin Panel</span>
			</a>
			<a href="/audit-logs" class="flex items-center gap-3 px-3 py-2 rounded-lg {currentPage === 'audit-logs' ? 'bg-purple-50 text-purple-700' : 'text-gray-600'} hover:bg-purple-50 hover:text-purple-700 transition-colors">
				<ScrollText class="w-5 h-5" />
				<span class="hidden lg:block {sidebarExpanded ? 'block' : 'hidden'}">Audit Logs</span>
			</a>
		{/if}
	</nav>
</aside>