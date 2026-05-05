<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { user, setUser } from '../../stores';
	import Navbar from '$lib/widgets/Navbar.svelte';
	import Sidebar from '$lib/widgets/Sidebar.svelte';
	import ApprovalPending from '$lib/components/ApprovalPending.svelte';
	import { API_BASE_URL } from '$lib/config';
	import { 
		Leaf, 
		Bell, 
		Settings, 
		User,
		Moon,
		Sun,
		BarChart3,
		TrendingUp,
		Zap,
		Recycle,
		Factory,
		Home as HomeIcon,
		Car,
		Plane,
		Lightbulb,
		Target,
		Award,
		ChevronRight,
		Download,
		Filter,
		RefreshCw
	} from 'lucide-svelte';

	let sidebarExpanded = false;
	let darkMode = false;
	let lastUpdated = "Just now";
	let currentUser: any | null = null;
	let loading = true;
	let chartFilter: 'daily' | 'weekly' | 'monthly' = 'monthly';
	let isApproved = true; // Track if user is approved

	// Dashboard data - will be populated from API
	let totalEmissions = 0;
	let emissionReduction = 0;
	let energyUsage = 0;
	let offsetAchieved = 0;

	let emissionsData: Array<{ month: string; emissions: number }> = [];
	let breakdownData: Array<{ scope: string; percentage: number }> = [];
	let topCategories: Array<{ category_name: string; total_emissions: number; location_count: number }> = [];

	let aiInsights: Array<{ text: string; type: string }> = [
		{ text: "Loading insights from your organization data...", type: "info" }
	];

	let recommendations: Array<{ title: string; impact: string; co2Saved: string; locations: number }> = [];

	let leaderboard = [
		{ name: "Loading leaderboard...", reduction: 0, badge: "" }
	];

	onMount(() => {
		// Check if user is logged in
		const userData = sessionStorage.getItem('user');
		if (userData) {
			try {
				const parsedUser = JSON.parse(userData);
				setUser(parsedUser);
				currentUser = parsedUser;
				
				// Check if user is approved
				if (parsedUser.status !== 'approved') {
					isApproved = false;
					loading = false;
					return;
				}
				
				// Fetch dashboard data
				fetchDashboardData();
			} catch (e) {
				console.error('Failed to parse user data:', e);
				goto('/');
			}
		} else {
			// Redirect to login if no user data
			goto('/');
		}
	});

	async function fetchDashboardData() {
		if (!currentUser || !currentUser.user_id) return;
		
		loading = true;
		try {
			// Fetch all data in parallel for faster loading
			const [statsResponse, emissionsResponse, breakdownResponse, categoriesResponse] = await Promise.all([
				fetch(`${API_BASE_URL}/dashboard/stats?user_id=${currentUser.user_id}`),
				fetch(`${API_BASE_URL}/dashboard/emissions-over-time?user_id=${currentUser.user_id}&filter=${chartFilter}`),
				fetch(`${API_BASE_URL}/dashboard/breakdown?user_id=${currentUser.user_id}&filter=${chartFilter}`),
				fetch(`${API_BASE_URL}/dashboard/top-categories?user_id=${currentUser.user_id}&filter=${chartFilter}`)
			]);
			
			// Check if user is not approved
			if (statsResponse.status === 403) {
				isApproved = false;
				loading = false;
				return;
			}
			
			// Parse all responses in parallel
			const [statsData, emissionsTimeData, breakdownDataResp, categoriesData] = await Promise.all([
				statsResponse.json(),
				emissionsResponse.json(),
				breakdownResponse.json(),
				categoriesResponse.json()
			]);
			
			// Update stats
			if (statsData.success) {
				totalEmissions = statsData.stats.total_emissions;
				emissionReduction = statsData.stats.emission_reduction;
				energyUsage = statsData.stats.energy_usage;
				offsetAchieved = statsData.stats.offset_achieved;
			}

			// Update emissions over time
			if (emissionsTimeData.success && emissionsTimeData.data.length > 0) {
				emissionsData = emissionsTimeData.data;
			} else {
				emissionsData = [{ month: 'No Data', emissions: 0 }];
			}

			// Update breakdown
			if (breakdownDataResp.success) {
				breakdownData = breakdownDataResp.data;
			}

			// Update top categories and generate insights
			if (categoriesData.success && categoriesData.data.length > 0) {
				topCategories = categoriesData.data;
				generateRecommendations();
				generateInsights();
			}

			lastUpdated = new Date().toLocaleTimeString();
		} catch (error) {
			console.error('Error fetching dashboard data:', error);
		} finally {
			loading = false;
		}
	}

	function generateRecommendations() {
		recommendations = topCategories.map((cat, idx) => {
			const impacts = ['High', 'Medium', 'Low'];
			const potentialSavings = (cat.total_emissions * 0.15).toFixed(0);
			return {
				title: `Optimize ${cat.category_name}`,
				impact: impacts[idx] || 'Medium',
				co2Saved: `${potentialSavings} kg`,
				locations: cat.location_count
			};
		});
	}

	function generateInsights() {
		aiInsights = [];
		
		if (emissionReduction > 0) {
			aiInsights.push({
				text: `Great work! Your emissions reduced by ${emissionReduction.toFixed(1)}% compared to last month.`,
				type: "success"
			});
		} else if (emissionReduction < 0) {
			aiInsights.push({
				text: `Emissions increased by ${Math.abs(emissionReduction).toFixed(1)}% this month. Review high-impact areas.`,
				type: "warning"
			});
		}

		if (topCategories.length > 0) {
			const topCat = topCategories[0];
			aiInsights.push({
				text: `${topCat.category_name} is your highest emission source at ${topCat.total_emissions.toFixed(0)} kg CO₂.`,
				type: "info"
			});
		}

		if (energyUsage > 0) {
			aiInsights.push({
				text: `Energy consumption is ${energyUsage.toFixed(0)} kWh this month. Consider renewable energy sources.`,
				type: "suggestion"
			});
		}

		if (aiInsights.length === 0) {
			aiInsights.push({
				text: "No data available yet. Start tracking emissions to see insights.",
				type: "info"
			});
		}
	}

	function toggleSidebar() {
		sidebarExpanded = !sidebarExpanded;
	}

	function toggleDarkMode() {
		darkMode = !darkMode;
	}

	function setChartFilter(filter: 'daily' | 'weekly' | 'monthly') {
		chartFilter = filter;
		// Refetch data based on the filter
		if (currentUser && currentUser.user_id) {
			fetchDashboardData();
		}
	}

	function getMaxEmission(data: Array<{ month: string; emissions: number }>) {
		if (!data || data.length === 0) return 3000;
		const max = Math.max(...data.map((d: { emissions: number }) => d.emissions || 0));
		return max > 0 ? Math.ceil(max * 1.1) : 3000; // Add 10% padding and round up
	}
</script>

<svelte:head>
	<title>Dashboard - CarbonTrack</title>
</svelte:head>

{#if !isApproved && currentUser}
	<!-- Show Approval Pending Screen -->
	<ApprovalPending userStatus={currentUser.status} userName={currentUser.name} />
{:else}
<div class="min-h-screen bg-gray-50 {darkMode ? 'dark' : ''}">
	<!-- Top Navigation Bar -->
	<Navbar {toggleSidebar} />

	<!-- Layout Container -->
	<div class="flex pt-16">
		<!-- Left Sidebar -->
		<Sidebar {sidebarExpanded} currentPage="dashboard" />

		<!-- Main Content -->
		<main class="flex-1 ml-16 lg:ml-64 p-6 space-y-6">
			<!-- Header Info Cards -->
			<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
				<!-- Total Emissions Card -->
				<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
					<div class="flex items-center justify-between mb-4">
						<div class="p-2 bg-red-100 rounded-lg">
							<Factory class="w-6 h-6 text-red-600" />
						</div>
					</div>
					<div class="space-y-1">
						<p class="text-2xl font-bold text-gray-900">{totalEmissions.toLocaleString()}</p>
						<p class="text-sm text-gray-500">Total Emissions (kg CO₂)</p>
						<p class="text-xs text-red-600">vs. last month +8%</p>
					</div>
				</div>

				<!-- Emission Reduction Card -->
				<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
					<div class="flex items-center justify-between mb-4">
						<div class="p-2 bg-green-100 rounded-lg">
							<TrendingUp class="w-6 h-6 text-green-600" />
						</div>
					</div>
					<div class="space-y-1">
						<p class="text-2xl font-bold text-gray-900">{emissionReduction}%</p>
						<p class="text-sm text-gray-500">Emission Reduction This Month</p>
						<p class="text-xs text-green-600">vs. last month +4%</p>
					</div>
				</div>

				<!-- Energy Usage Card -->
				<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
					<div class="flex items-center justify-between mb-4">
						<div class="p-2 bg-yellow-100 rounded-lg">
							<Zap class="w-6 h-6 text-yellow-600" />
						</div>
					</div>
					<div class="space-y-1">
						<p class="text-2xl font-bold text-gray-900">{energyUsage.toLocaleString()}</p>
						<p class="text-sm text-gray-500">Energy Usage (kWh)</p>
						<p class="text-xs text-yellow-600">vs. last month -2%</p>
					</div>
				</div>

				<!-- Offset Achieved Card -->
				<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
					<div class="flex items-center justify-between mb-4">
						<div class="p-2 bg-teal-100 rounded-lg">
							<Recycle class="w-6 h-6 text-teal-600" />
						</div>
					</div>
					<div class="space-y-1">
						<p class="text-2xl font-bold text-gray-900">{offsetAchieved}</p>
						<p class="text-sm text-gray-500">Offset Achieved (kg CO₂)</p>
						<p class="text-xs text-teal-600">vs. last month +15%</p>
					</div>
				</div>
			</div>

			<!-- Main Analytics Section -->
			<div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
				<!-- Emissions Chart -->
				<div class="xl:col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-100">
					<div class="flex items-center justify-between mb-6">
						<h3 class="text-lg font-semibold text-gray-900">Emissions Over Time</h3>
						<div class="flex items-center gap-2">
							<button 
								on:click={() => setChartFilter('daily')}
								class="px-3 py-1 text-sm {chartFilter === 'daily' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-600'} rounded-lg hover:bg-green-700 hover:text-white transition-colors">
								Daily
							</button>
							<button 
								on:click={() => setChartFilter('weekly')}
								class="px-3 py-1 text-sm {chartFilter === 'weekly' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-600'} rounded-lg hover:bg-green-700 hover:text-white transition-colors">
								Weekly
							</button>
							<button 
								on:click={() => setChartFilter('monthly')}
								class="px-3 py-1 text-sm {chartFilter === 'monthly' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-600'} rounded-lg hover:bg-green-700 hover:text-white transition-colors">
								Monthly
							</button>
						</div>
					</div>
					
					<!-- Simple Chart Visualization -->
					{#if loading}
						<div class="h-64 flex items-center justify-center">
							<RefreshCw class="w-8 h-8 text-gray-400 animate-spin" />
						</div>
					{:else if emissionsData.length > 0 && emissionsData[0].month !== 'No Data'}
						<div class="h-72 relative pb-8">
							<!-- Y-axis labels -->
							<div class="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-gray-500 w-14 text-right pr-2">
								<span>{getMaxEmission(emissionsData).toLocaleString()}</span>
								<span>{Math.round(getMaxEmission(emissionsData) * 0.75).toLocaleString()}</span>
								<span>{Math.round(getMaxEmission(emissionsData) * 0.5).toLocaleString()}</span>
								<span>{Math.round(getMaxEmission(emissionsData) * 0.25).toLocaleString()}</span>
								<span>0</span>
							</div>
							
							<!-- Chart bars -->
							<div class="h-full ml-16 flex items-end justify-between gap-1 pb-6 border-b border-l border-gray-200">
								{#each emissionsData as data, i}
									<div class="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
										<div 
											class="bg-gradient-to-t from-green-600 to-green-400 rounded-t w-full transition-all duration-500 hover:from-green-700 hover:to-green-500 relative cursor-pointer shadow-sm"
											style="height: {data.emissions > 0 ? (data.emissions / getMaxEmission(emissionsData)) * 100 : 1}%;">
											<!-- Tooltip -->
											<div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
												<div class="bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap shadow-lg">
													{data.emissions.toFixed(0)} kg CO₂
												</div>
											</div>
										</div>
									</div>
								{/each}
							</div>
							
							<!-- X-axis labels -->
							<div class="absolute bottom-0 left-16 right-0 flex justify-between">
								{#each emissionsData as data, i}
									<span class="flex-1 text-center text-xs text-gray-500 font-medium">{data.month}</span>
								{/each}
							</div>
						</div>
					{:else}
						<div class="h-64 flex items-center justify-center">
							<div class="text-center">
								<BarChart3 class="w-12 h-12 text-gray-300 mx-auto mb-2" />
								<p class="text-sm text-gray-500">No emission data available</p>
								<p class="text-xs text-gray-400 mt-1">Start tracking to see your emissions over time</p>
							</div>
						</div>
					{/if}
				</div>

				<!-- AI Insights Panel -->
				<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">Insights</h3>
					<div class="space-y-4">
						{#each aiInsights as insight}
							<div class="p-4 rounded-lg {insight.type === 'warning' ? 'bg-orange-50 border border-orange-200' : insight.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-blue-50 border border-blue-200'}">
								<p class="text-sm {insight.type === 'warning' ? 'text-orange-800' : insight.type === 'success' ? 'text-green-800' : 'text-blue-800'}">{insight.text}</p>
							</div>
						{/each}
					</div>
				</div>
			</div>

			<!-- Bottom Section -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<!-- Emission Breakdown -->
				<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">Emission Breakdown</h3>
					{#if loading}
						<div class="flex items-center justify-center h-32">
							<RefreshCw class="w-6 h-6 text-gray-400 animate-spin" />
						</div>
					{:else if breakdownData.length > 0}
						<div class="flex flex-col items-center">
							<!-- Pie Chart -->
							<svg viewBox="0 0 200 200" class="w-48 h-48 mb-4">
								{#each breakdownData as item, i}
									{@const colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']}
									{@const color = colors[i % colors.length]}
									{@const startAngle = breakdownData.slice(0, i).reduce((sum, d) => sum + (d.percentage / 100 * 360), 0)}
									{@const angle = item.percentage / 100 * 360}
									{@const endAngle = startAngle + angle}
									{@const largeArcFlag = angle > 180 ? 1 : 0}
									{@const startX = 100 + 80 * Math.cos((startAngle - 90) * Math.PI / 180)}
									{@const startY = 100 + 80 * Math.sin((startAngle - 90) * Math.PI / 180)}
									{@const endX = 100 + 80 * Math.cos((endAngle - 90) * Math.PI / 180)}
									{@const endY = 100 + 80 * Math.sin((endAngle - 90) * Math.PI / 180)}
									
									<path
										d="M 100 100 L {startX} {startY} A 80 80 0 {largeArcFlag} 1 {endX} {endY} Z"
										fill={color}
										stroke="white"
										stroke-width="2"
										class="hover:opacity-80 transition-opacity cursor-pointer"
									>
										<title>{item.scope}: {item.percentage.toFixed(1)}%</title>
									</path>
								{/each}
								
								<!-- Center circle for donut effect -->
								<circle cx="100" cy="100" r="50" fill="white" />
								
								<!-- Center text -->
								<text x="100" y="95" text-anchor="middle" class="text-xs fill-gray-400 font-medium">
									Total
								</text>
								<text x="100" y="110" text-anchor="middle" class="text-sm fill-gray-900 font-bold">
									100%
								</text>
							</svg>
							
							<!-- Legend -->
							<div class="space-y-2 w-full">
								{#each breakdownData as item, i}
									{@const colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']}
									{@const color = colors[i % colors.length]}
									<div class="flex items-center justify-between">
										<div class="flex items-center gap-2">
											<div class="w-3 h-3 rounded-full" style="background-color: {color}"></div>
											<span class="text-sm text-gray-600">{item.scope}</span>
										</div>
										<span class="text-sm font-medium text-gray-900">{item.percentage.toFixed(1)}%</span>
									</div>
								{/each}
							</div>
						</div>
					{:else}
						<p class="text-sm text-gray-500">No emission data available</p>
					{/if}
				</div>

				<!-- Recommendations -->
				<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
					{#if loading}
						<div class="flex items-center justify-center h-32">
							<RefreshCw class="w-6 h-6 text-gray-400 animate-spin" />
						</div>
					{:else if recommendations.length > 0}
						<div class="space-y-3">
							{#each recommendations as rec}
								<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
									<div class="flex-1">
										<p class="text-sm font-medium text-gray-900">{rec.title}</p>
										<p class="text-xs text-gray-500">Impact: {rec.impact} • Saves {rec.co2Saved}</p>
									</div>
									<ChevronRight class="w-4 h-4 text-gray-400" />
								</div>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-gray-500">Start tracking emissions to get recommendations</p>
					{/if}
				</div>

				<!-- Leaderboard -->
				<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">Your Progress</h3>
					<div class="space-y-3">
						<div class="flex items-center justify-between bg-green-50 rounded-lg p-3">
							<div class="flex items-center gap-3">
								<span class="text-lg">🎯</span>
								<div>
									<p class="text-sm font-medium text-gray-900">Current Month</p>
									<p class="text-xs text-gray-500">{emissionReduction >= 0 ? `${emissionReduction.toFixed(1)}% reduction` : `${Math.abs(emissionReduction).toFixed(1)}% increase`}</p>
								</div>
							</div>
						</div>
						<div class="flex items-center justify-between p-3">
							<div class="flex items-center gap-3">
								<span class="text-lg">📊</span>
								<div>
									<p class="text-sm font-medium text-gray-900">Total Emissions</p>
									<p class="text-xs text-gray-500">{totalEmissions.toFixed(0)} kg CO₂</p>
								</div>
							</div>
						</div>
						<div class="flex items-center justify-between p-3">
							<div class="flex items-center gap-3">
								<span class="text-lg">⚡</span>
								<div>
									<p class="text-sm font-medium text-gray-900">Energy Usage</p>
									<p class="text-xs text-gray-500">{energyUsage.toFixed(0)} kWh</p>
								</div>
							</div>
						</div>
						<div class="flex items-center justify-between p-3">
							<div class="flex items-center gap-3">
								<span class="text-lg">🌱</span>
								<div>
									<p class="text-sm font-medium text-gray-900">Offset Achieved</p>
									<p class="text-xs text-gray-500">{offsetAchieved.toFixed(0)} kg CO₂</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Export Actions -->
			<div class="flex items-center justify-between bg-white rounded-xl p-4 shadow-sm border border-gray-100">
				<p class="text-sm text-gray-600">Export your sustainability data</p>
				<div class="flex items-center gap-2">
					<button class="px-4 py-2 text-sm bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
						<Download class="w-4 h-4 inline mr-1" />
						CSV
					</button>
					<button class="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
						<Download class="w-4 h-4 inline mr-1" />
						PDF Report
					</button>
				</div>
			</div>
		</main>
	</div>
</div>
{/if}