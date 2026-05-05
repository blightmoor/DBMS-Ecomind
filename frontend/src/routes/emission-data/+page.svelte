<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Navbar from '$lib/widgets/Navbar.svelte';
	import Sidebar from '$lib/widgets/Sidebar.svelte';
	import ApprovalPending from '$lib/components/ApprovalPending.svelte';
	import { API_BASE_URL } from '$lib/config';
	import { 
		Calendar, 
		Filter, 
		TrendingUp, 
		TrendingDown, 
		BarChart3, 
		PieChart, 
		Download, 
		Search,
		ArrowUpRight,
		ArrowDownRight,
		Zap,
		Car,
		Factory,
		Home,
		Leaf,
		Bell,
		Settings,
		User,
		Menu,
		X,
		RefreshCw
	} from 'lucide-svelte';

	let sidebarExpanded = false;
	let currentUser: any | null = null;
	let loading = true;
	let isApproved = true;
	
	function toggleSidebar() {
		sidebarExpanded = !sidebarExpanded;
	}
	
	// New filter states
	let startDate = '';
	let endDate = '';
	let selectedLocationIds: number[] = [];
	let selectedCategoryIds: number[] = [];
	let searchQuery = '';

	// Available filter options from API
	let locations: Array<{ location_id: number; name: string }> = [];
	let categories: Array<{ category_id: number; name: string }> = [];

	// Data from API
	let summaryStats = {
		totalEmissions: 0,
		averagePerDay: 0,
		changeFromLastWeek: 0
	};

	interface EmissionOverTime {
		date: string;
		category: string;
		category_id: number;
		value: number;
	}

	let emissionsOverTime: EmissionOverTime[] = [];
	let categoryBreakdown: Array<{ category: string; category_id: number; value: number; color: string; icon: any }> = [];
	let emissionRecords: Array<{ id: number; date: string; source: string; category: string; value: number; unit: string }> = [];

	let sortColumn = 'date';
	let sortDirection = 'desc';

	// Category icon mapping
	const categoryIcons: Record<string, any> = {
		'Transport': Car,
		'Energy': Zap,
		'Industry': Factory,
		'Residential': Home,
		'Electricity': Zap,
		'Manufacturing': Factory,
		'Heating': Home,
		'Fleet': Car
	};

	const categoryColors: Record<string, string> = {
		'Transport': '#10B981',
		'Energy': '#F59E0B',
		'Industry': '#EF4444',
		'Residential': '#8B5CF6',
		'Electricity': '#F59E0B',
		'Manufacturing': '#EF4444',
		'Heating': '#8B5CF6',
		'Fleet': '#10B981'
	};

	// Generate colors for categories dynamically
	const colorPalette = ['#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#3B82F6', '#EC4899', '#14B8A6', '#F97316'];
	
	function getCategoryColor(categoryId: number): string {
		return colorPalette[categoryId % colorPalette.length];
	}

	onMount(() => {
		// Check if user is logged in
		const userData = sessionStorage.getItem('user');
		if (userData) {
			try {
				const parsedUser = JSON.parse(userData);
				currentUser = parsedUser;
				
				// Check if user is approved
				if (currentUser.status !== 'approved') {
					isApproved = false;
					loading = false;
					return;
				}
				
				// Set default date range (last 30 days)
				const today = new Date();
				endDate = today.toISOString().split('T')[0];
				const thirtyDaysAgo = new Date(today);
				thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
				startDate = thirtyDaysAgo.toISOString().split('T')[0];
				
				fetchEmissionData();
			} catch (e) {
				console.error('Failed to parse user data:', e);
				goto('/');
			}
		} else {
			goto('/');
		}
	});

	async function fetchEmissionData() {
		if (!currentUser || !currentUser.user_id) return;
		
		loading = true;
		try {
			// Build query parameters
			let url = `${API_BASE_URL}/emission-data/records?user_id=${currentUser.user_id}`;
			
			if (startDate) url += `&start_date=${startDate}`;
			if (endDate) url += `&end_date=${endDate}`;
			if (selectedLocationIds.length > 0) url += `&location_ids=${selectedLocationIds.join(',')}`;
			if (selectedCategoryIds.length > 0) url += `&category_ids=${selectedCategoryIds.join(',')}`;
			
			const response = await fetch(url);
			
			// Check if user is not approved
			if (response.status === 403) {
				isApproved = false;
				loading = false;
				return;
			}
			
			const data = await response.json();
			
			if (data.success) {
				// Update summary stats
				summaryStats = {
					totalEmissions: data.summary.total_emissions,
					averagePerDay: data.summary.average_per_day,
					changeFromLastWeek: data.summary.change_from_last_period
				};

				// Update emissions over time (grouped by category)
				emissionsOverTime = data.emissions_over_time;

				// Update category breakdown with icons and colors
				categoryBreakdown = data.category_breakdown.map((cat: any) => ({
					category: cat.category,
					category_id: cat.category_id,
					value: cat.value,
					color: categoryColors[cat.category] || getCategoryColor(cat.category_id),
					icon: categoryIcons[cat.category] || Factory
				}));

				// Update emission records (not filtered)
				emissionRecords = data.records;
				
				// Update filter options
				locations = data.locations || [];
				categories = data.categories || [];
			}
		} catch (error) {
			console.error('Error fetching emission data:', error);
		} finally {
			loading = false;
		}
	}

	// Watch for filter changes
	$: if (currentUser && (startDate || endDate || selectedLocationIds || selectedCategoryIds)) {
		fetchEmissionData();
	}

	// Toggle category selection
	function toggleCategory(categoryId: number) {
		const index = selectedCategoryIds.indexOf(categoryId);
		if (index === -1) {
			selectedCategoryIds = [...selectedCategoryIds, categoryId];
		} else {
			selectedCategoryIds = selectedCategoryIds.filter(id => id !== categoryId);
		}
	}

	// Filter records based on search only (Recent Emissions not affected by other filters)
	$: filteredRecords = emissionRecords.filter(record => {
		const matchesSearch = searchQuery === '' || 
			record.source.toLowerCase().includes(searchQuery.toLowerCase()) ||
			record.category.toLowerCase().includes(searchQuery.toLowerCase());
		
		return matchesSearch;
	});

	function sortData(column: string) {
		if (sortColumn === column) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortColumn = column;
			sortDirection = 'asc';
		}

		filteredRecords = [...filteredRecords].sort((a: any, b: any) => {
			let aVal = a[column];
			let bVal = b[column];

			if (column === 'value') {
				aVal = parseFloat(aVal);
				bVal = parseFloat(bVal);
			}

			if (sortDirection === 'asc') {
				return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
			} else {
				return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
			}
		});
	}

	// Prepare data for multi-line chart
	interface ChartData {
		dates: string[];
		categories: Array<{
			category: string;
			category_id: number;
			color: string;
			points: number[];
		}>;
	}

	$: chartData = (() => {
		if (emissionsOverTime.length === 0) return { dates: [], categories: [] };

		// Get unique dates and categories
		const uniqueDates = [...new Set(emissionsOverTime.map(e => e.date))].sort();
		const uniqueCategories = [...new Set(emissionsOverTime.map(e => e.category_id))];

		// Build data structure
		const categoriesData = uniqueCategories.map(catId => {
			const categoryEntry = emissionsOverTime.find(e => e.category_id === catId);
			const categoryName = categoryEntry?.category || 'Unknown';
			const color = categoryBreakdown.find(c => c.category_id === catId)?.color || getCategoryColor(catId);

			const points = uniqueDates.map(date => {
				const entry = emissionsOverTime.find(e => e.date === date && e.category_id === catId);
				return entry ? entry.value : 0;
			});

			return {
				category: categoryName,
				category_id: catId,
				color,
				points
			};
		});

		return {
			dates: uniqueDates,
			categories: categoriesData
		};
	})();

	// Calculate max value for chart scaling
	$: maxChartValue = chartData.categories.length > 0 
		? Math.max(...chartData.categories.flatMap(c => c.points)) 
		: 0;
</script>

<svelte:head>
	<title>Emission Data - CarbonTrack</title>
</svelte:head>

{#if !isApproved && currentUser}
	<!-- Show Approval Pending Screen -->
	<ApprovalPending userStatus={currentUser.status} userName={currentUser.name} />
{:else}
<div class="min-h-screen bg-gray-50">
	<!-- Top Navigation -->
	<Navbar {toggleSidebar} />

	<!-- Sidebar -->
	<Sidebar {sidebarExpanded} currentPage="emission-data" />

	<!-- Main Content -->
	<div class="lg:ml-64 pt-16">
		<div class="p-6 space-y-6">
			<!-- Header Section -->
			<div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
				<div>
					<h1 class="text-3xl font-bold text-gray-900 mb-2">Emission Data</h1>
					<p class="text-gray-600">Track and analyze your carbon footprint across all sources</p>
				</div>
				
				<!-- Filters -->
				<div class="flex flex-wrap items-center gap-4">
					<!-- Date Range Filter -->
					<div class="flex items-center space-x-2">
						<Calendar class="w-5 h-5 text-gray-500" />
						<input 
							type="date" 
							bind:value={startDate}
							class="bg-white border border-gray-300 text-gray-900 px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
							placeholder="Start Date"
						/>
						<span class="text-gray-500">to</span>
						<input 
							type="date" 
							bind:value={endDate}
							class="bg-white border border-gray-300 text-gray-900 px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
							placeholder="End Date"
						/>
					</div>
					
					<!-- Location Filter -->
					<div class="flex items-center space-x-2">
						<Filter class="w-5 h-5 text-gray-500" />
						<select 
							on:change={(e) => {
								const value = e.currentTarget.value;
								selectedLocationIds = value === 'all' ? [] : [parseInt(value)];
							}}
							class="bg-white border border-gray-300 text-gray-900 px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
						>
							<option value="all">All Locations</option>
							{#each locations as location}
								<option value={location.location_id}>{location.name}</option>
							{/each}
						</select>
					</div>
					
					<!-- Category Multi-Select (Dropdown with checkboxes) -->
					<div class="relative">
						<details class="group">
							<summary class="list-none cursor-pointer bg-white border border-gray-300 text-gray-900 px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 flex items-center justify-between min-w-[150px]">
								<span>
									{selectedCategoryIds.length === 0 ? 'All Categories' : `${selectedCategoryIds.length} Selected`}
								</span>
								<svg class="w-4 h-4 ml-2 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
								</svg>
							</summary>
							<div class="absolute z-10 mt-2 bg-white border border-gray-300 rounded-lg shadow-lg min-w-[200px] max-h-64 overflow-y-auto">
								{#each categories as category}
									<label class="flex items-center px-4 py-2 hover:bg-gray-50 cursor-pointer">
										<input 
											type="checkbox" 
											checked={selectedCategoryIds.includes(category.category_id)}
											on:change={() => toggleCategory(category.category_id)}
											class="mr-3 text-green-600 focus:ring-green-500"
										/>
										<span class="text-gray-900">{category.name}</span>
									</label>
								{/each}
								{#if categories.length === 0}
									<div class="px-4 py-2 text-gray-500 text-sm">No categories available</div>
								{/if}
							</div>
						</details>
					</div>
				</div>
			</div>

			<!-- Summary Cards -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
				<div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-all">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-500 text-sm">Total Emissions</p>
							{#if loading}
								<div class="h-9 w-24 bg-gray-200 animate-pulse rounded mt-1"></div>
							{:else}
								<p class="text-3xl font-bold text-gray-900">{summaryStats.totalEmissions.toLocaleString()}</p>
							{/if}
							<p class="text-gray-500 text-sm">kg CO₂</p>
						</div>
						<div class="p-3 bg-green-50 rounded-lg">
							<TrendingUp class="w-8 h-8 text-green-600" />
						</div>
					</div>
				</div>

				<div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-all">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-500 text-sm">Average per Day</p>
							{#if loading}
								<div class="h-9 w-24 bg-gray-200 animate-pulse rounded mt-1"></div>
							{:else}
								<p class="text-3xl font-bold text-gray-900">{summaryStats.averagePerDay.toLocaleString()}</p>
							{/if}
							<p class="text-gray-500 text-sm">kg CO₂/day</p>
						</div>
						<div class="p-3 bg-blue-50 rounded-lg">
							<BarChart3 class="w-8 h-8 text-blue-600" />
						</div>
					</div>
				</div>

				<div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-all">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-500 text-sm">Change from Last Period</p>
							{#if loading}
								<div class="h-9 w-24 bg-gray-200 animate-pulse rounded mt-1"></div>
							{:else}
								<p class="text-3xl font-bold text-gray-900 flex items-center">
									{Math.abs(summaryStats.changeFromLastWeek).toFixed(1)}%
									{#if summaryStats.changeFromLastWeek < 0}
										<ArrowDownRight class="w-6 h-6 text-green-500 ml-2" />
									{:else}
										<ArrowUpRight class="w-6 h-6 text-red-500 ml-2" />
									{/if}
								</p>
								<p class="text-gray-500 text-sm">
									{summaryStats.changeFromLastWeek < 0 ? 'Decrease' : 'Increase'}
								</p>
							{/if}
						</div>
						<div class="p-3 bg-{summaryStats.changeFromLastWeek < 0 ? 'green' : 'red'}-50 rounded-lg">
							{#if summaryStats.changeFromLastWeek < 0}
								<TrendingDown class="w-8 h-8 text-green-500" />
							{:else}
								<TrendingUp class="w-8 h-8 text-red-500" />
							{/if}
						</div>
					</div>
				</div>
			</div>

			<!-- Charts Section -->
			<div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
				<!-- Multi-Line Emissions Chart -->
				<div class="bg-white border border-gray-200 rounded-xl p-6">
					<div class="flex items-center justify-between mb-6">
						<h3 class="text-xl font-semibold text-gray-900">Emissions by Category</h3>
						<button class="p-2 text-gray-500 hover:text-gray-700 transition-colors">
							<Download class="w-5 h-5" />
						</button>
					</div>
					
					{#if loading}
						<div class="h-64 flex items-center justify-center">
							<RefreshCw class="w-8 h-8 text-gray-400 animate-spin" />
						</div>
					{:else if chartData.dates.length > 0 && chartData.categories.length > 0}
						<div class="space-y-4">
							<!-- Chart Legend -->
							<div class="flex flex-wrap gap-4">
								{#each chartData.categories as category}
									<div class="flex items-center space-x-2">
										<div class="w-3 h-3 rounded-full" style="background-color: {category.color}"></div>
										<span class="text-sm text-gray-700">{category.category}</span>
									</div>
								{/each}
							</div>
							
							<!-- SVG Multi-Line Chart -->
							<svg viewBox="0 0 800 300" class="w-full h-64">
								<!-- Grid lines -->
								{#each Array(5) as _, i}
									<line 
										x1="50" 
										y1={50 + i * 50} 
										x2="750" 
										y2={50 + i * 50} 
										stroke="#E5E7EB" 
										stroke-width="1"
									/>
									<text 
										x="40" 
										y={55 + i * 50} 
										text-anchor="end" 
										font-size="12" 
										fill="#6B7280"
									>
										{Math.round(maxChartValue * (1 - i * 0.25))}
									</text>
								{/each}
								
								<!-- Lines for each category -->
								{#each chartData.categories as category}
									{@const points = category.points.map((value, i) => ({
										x: 50 + (i * (700 / (chartData.dates.length - 1 || 1))),
										y: 250 - (value / maxChartValue * 200)
									}))}
									
									<!-- Line path -->
									<polyline 
										points={points.map(p => `${p.x},${p.y}`).join(' ')}
										fill="none"
										stroke={category.color}
										stroke-width="2.5"
										stroke-linecap="round"
										stroke-linejoin="round"
									/>
									
									<!-- Data points -->
									{#each points as point, i}
										<circle 
											cx={point.x} 
											cy={point.y} 
											r="4" 
											fill={category.color}
										>
											<title>{category.category}: {category.points[i]} kg CO₂</title>
										</circle>
									{/each}
								{/each}
								
								<!-- X-axis labels -->
								{#each chartData.dates as date, i}
									{#if i % Math.ceil(chartData.dates.length / 8) === 0}
										<text 
											x={50 + (i * (700 / (chartData.dates.length - 1 || 1)))} 
											y="280" 
											text-anchor="middle" 
											font-size="11" 
											fill="#6B7280"
										>
											{new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
										</text>
									{/if}
								{/each}
							</svg>
						</div>
					{:else}
						<div class="h-64 flex items-center justify-center">
							<div class="text-center">
								<BarChart3 class="w-12 h-12 text-gray-300 mx-auto mb-2" />
								<p class="text-sm text-gray-500">No emission data available</p>
							</div>
						</div>
					{/if}
				</div>

				<!-- Category Breakdown Chart -->
				<div class="bg-white border border-gray-200 rounded-xl p-6">
					<div class="flex items-center justify-between mb-6">
						<h3 class="text-xl font-semibold text-gray-900">Category Breakdown</h3>
						<PieChart class="w-5 h-5 text-gray-500" />
					</div>
					
					{#if loading}
						<div class="h-64 flex items-center justify-center">
							<RefreshCw class="w-6 h-6 text-gray-400 animate-spin" />
						</div>
					{:else if categoryBreakdown.length > 0}
						<div class="space-y-4">
							{#each categoryBreakdown as category}
								<div class="flex items-center justify-between">
									<div class="flex items-center space-x-3">
										<div class="p-2 rounded-lg" style="background-color: {category.color}20">
											<svelte:component this={category.icon} class="w-5 h-5" style="color: {category.color}" />
										</div>
										<span class="text-gray-900 font-medium">{category.category}</span>
									</div>
									<div class="text-right">
										<p class="text-gray-900 font-semibold">{category.value.toLocaleString()} kg</p>
										<div class="w-24 h-2 bg-gray-200 rounded-full mt-1">
											<div 
												class="h-full rounded-full transition-all duration-500"
												style="background-color: {category.color}; width: {categoryBreakdown.length > 0 ? (category.value / Math.max(...categoryBreakdown.map(c => c.value))) * 100 : 0}%"
											></div>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="h-64 flex items-center justify-center">
							<div class="text-center">
								<PieChart class="w-12 h-12 text-gray-300 mx-auto mb-2" />
								<p class="text-sm text-gray-500">No category data available</p>
							</div>
						</div>
					{/if}
				</div>
			</div>

			<!-- Data Table -->
			<div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
				<div class="p-6 border-b border-gray-200">
					<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
						<h3 class="text-xl font-semibold text-gray-900">Recent Emissions</h3>
						<div class="flex items-center space-x-4">
							<div class="relative">
								<Search class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
								<input 
									type="text" 
									placeholder="Search emissions..."
									bind:value={searchQuery}
									class="bg-gray-50 border border-gray-300 text-gray-900 pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
								/>
							</div>
							<button class="p-2 text-gray-500 hover:text-gray-700 transition-colors">
								<Download class="w-5 h-5" />
							</button>
						</div>
					</div>
				</div>

				<div class="overflow-x-auto">
					{#if loading}
						<div class="h-64 flex items-center justify-center">
							<RefreshCw class="w-8 h-8 text-gray-400 animate-spin" />
						</div>
					{:else if filteredRecords.length > 0}
						<table class="w-full">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-6 py-4 text-left">
										<button on:click={() => sortData('date')} class="flex items-center space-x-1 text-gray-600 hover:text-gray-900 transition-colors">
											<span>Date</span>
											{#if sortColumn === 'date'}
												{#if sortDirection === 'asc'}
													<ArrowUpRight class="w-4 h-4" />
												{:else}
													<ArrowDownRight class="w-4 h-4" />
												{/if}
											{/if}
										</button>
									</th>
									<th class="px-6 py-4 text-left">
										<button on:click={() => sortData('source')} class="flex items-center space-x-1 text-gray-600 hover:text-gray-900 transition-colors">
											<span>Source</span>
											{#if sortColumn === 'source'}
												{#if sortDirection === 'asc'}
													<ArrowUpRight class="w-4 h-4" />
												{:else}
													<ArrowDownRight class="w-4 h-4" />
												{/if}
											{/if}
										</button>
									</th>
									<th class="px-6 py-4 text-left">
										<button on:click={() => sortData('category')} class="flex items-center space-x-1 text-gray-600 hover:text-gray-900 transition-colors">
											<span>Category</span>
											{#if sortColumn === 'category'}
												{#if sortDirection === 'asc'}
													<ArrowUpRight class="w-4 h-4" />
												{:else}
													<ArrowDownRight class="w-4 h-4" />
												{/if}
											{/if}
										</button>
									</th>
									<th class="px-6 py-4 text-right">
										<button on:click={() => sortData('value')} class="flex items-center justify-end space-x-1 text-gray-600 hover:text-gray-900 transition-colors">
											<span>Emissions</span>
											{#if sortColumn === 'value'}
												{#if sortDirection === 'asc'}
													<ArrowUpRight class="w-4 h-4" />
												{:else}
													<ArrowDownRight class="w-4 h-4" />
												{/if}
											{/if}
										</button>
									</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-200">
								{#each filteredRecords as record}
									<tr class="hover:bg-gray-50 transition-colors">
										<td class="px-6 py-4 text-gray-600">
											{new Date(record.date).toLocaleDateString()}
										</td>
										<td class="px-6 py-4 text-gray-900 font-medium">
											{record.source}
										</td>
										<td class="px-6 py-4">
											<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
												{record.category}
											</span>
										</td>
										<td class="px-6 py-4 text-right text-gray-900 font-semibold">
											{record.value.toFixed(2)} {record.unit}
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					{:else}
						<div class="h-64 flex items-center justify-center">
							<div class="text-center">
								<BarChart3 class="w-12 h-12 text-gray-300 mx-auto mb-2" />
								<p class="text-sm text-gray-500">No emission records found</p>
								<p class="text-xs text-gray-400 mt-1">Try adjusting your search</p>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>
{/if}

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