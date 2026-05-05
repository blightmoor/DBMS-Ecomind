<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Navbar from '$lib/widgets/Navbar.svelte';
	import Sidebar from '$lib/widgets/Sidebar.svelte';
	import ApprovalPending from '$lib/components/ApprovalPending.svelte';
	import { API_BASE_URL } from '$lib/config';
	import { 
		Brain,
		TrendingUp,
		TrendingDown,
		Zap,
		AlertTriangle,
		Target,
		Sparkles,
		BarChart3,
		Activity,
		Bot,
		RefreshCw,
		ArrowRight,
		Calendar,
		MapPin,
		Car,
		Home,
		Factory,
		Lightbulb,
		CheckCircle,
		Clock,
		ArrowUp,
		ArrowDown,
		Leaf
	} from 'lucide-svelte';
	import { user, setUser } from '../../stores';

	let sidebarExpanded = false;
	let isGeneratingInsight = false;
	let isLoading = true;
	let errorMessage = '';
	let isApproved = true; // Track if user is approved
	
	function toggleSidebar() {
		sidebarExpanded = !sidebarExpanded;
	}

	// Get user from store
	let currentUser: any | null = null;
	let userId: number | null = null;


	// AI Insights data
	type TrendPoint = {
		month: string;
		actual: number | null;
		predicted: number | null;
	};
	let keyPredictions = {
		nextMonthEmissions: { value: 0, change: 0, trend: 'down' },
		nextMonthEnergy: { value: 0, change: 0, trend: 'down' },
		topRiskSources: [] as string[]
	};

	let emissionsTrendData: TrendPoint[] = [];
	let energyTrendData: TrendPoint[] = [];
	let aiInsights: any[] = [];
	let insightsGenerated = 0;

	// Icon mapping for dynamic icons
	const iconMap: any = {
		'prediction': TrendingUp,
		'opportunity': Lightbulb,
		'alert': AlertTriangle,
		'warning': AlertTriangle,
		'success': CheckCircle
	};

	function getSeverityColor(severity: string) {
		switch(severity) {
			case 'high': return 'border-l-red-500 bg-red-50';
			case 'medium': return 'border-l-yellow-500 bg-yellow-50';
			case 'low': return 'border-l-green-500 bg-green-50';
			default: return 'border-l-gray-500 bg-gray-50';
		}
	}

	function getIconColor(severity: string) {
		switch(severity) {
			case 'high': return 'text-red-600';
			case 'medium': return 'text-yellow-600';
			case 'low': return 'text-green-600';
			default: return 'text-gray-600';
		}
	}

	function extractMaxValue(data: TrendPoint[]) {
		const values = data
			.flatMap(point => [point.actual, point.predicted])
			.filter((value): value is number => typeof value === 'number' && Number.isFinite(value));
		const max = Math.max(0, ...values);
		return max > 0 ? max : 1;
	}

	function getBarHeight(value: number | null | undefined, maxValue: number) {
		if (typeof value !== 'number' || !Number.isFinite(value) || maxValue <= 0) {
			return '3%';
		}
		const percentage = (value / maxValue) * 100;
		return `${Math.max(percentage, 3)}%`;
	}

	$: emissionsMaxValue = extractMaxValue(emissionsTrendData);
	$: energyMaxValue = extractMaxValue(energyTrendData);

	async function fetchPredictions() {
		try {
			const response = await fetch(`${API_BASE_URL}/ai-insights/predictions?user_id=${userId}`);
			
			// Check if user is not approved
			if (response.status === 403) {
				isApproved = false;
				return;
			}
			
			const data = await response.json();
			
			if (data.success) {
				keyPredictions = {
					nextMonthEmissions: data.predictions.next_month_emissions,
					nextMonthEnergy: data.predictions.next_month_energy,
					topRiskSources: data.predictions.top_risk_sources
				};
			}
		} catch (error) {
			console.error('Error fetching predictions:', error);
		}
	}

	async function fetchTrends() {
		try {
			// Fetch both emissions and energy trends in parallel
			const [emissionsResponse, energyResponse] = await Promise.all([
				fetch(`${API_BASE_URL}/ai-insights/trends?user_id=${userId}&data_type=emissions`),
				fetch(`${API_BASE_URL}/ai-insights/trends?user_id=${userId}&data_type=energy`)
			]);
			
			// Parse responses in parallel
			const [emissionsData, energyData] = await Promise.all([
				emissionsResponse.json(),
				energyResponse.json()
			]);
			
			if (emissionsData.success) {
				emissionsTrendData = emissionsData.trends;
			}
			
			if (energyData.success) {
				energyTrendData = energyData.trends;
			}
		} catch (error) {
			console.error('Error fetching trends:', error);
		}
	}

	async function fetchRecommendations() {
		try {
			const response = await fetch(`${API_BASE_URL}/ai-insights/recommendations?user_id=${userId}`);
			const data = await response.json();
			
			if (data.success) {
				aiInsights = data.insights.map((insight: any) => ({
					...insight,
					icon: iconMap[insight.type as string] || Brain
				}));
				insightsGenerated = data.total_count;
			}
		} catch (error) {
			console.error('Error fetching recommendations:', error);
		}
	}

	async function generateNewInsight() {
		isGeneratingInsight = true;
		
		try {
			const response = await fetch(`${API_BASE_URL}/ai-insights/generate?user_id=${userId}`, {
				method: 'POST'
			});
			const data = await response.json();
			
			if (data.success) {
				const newInsight = {
					...data.insight,
					icon: iconMap[data.insight.type as string] || Brain
				};
				
				aiInsights = [newInsight, ...aiInsights];
				insightsGenerated++;
			}
		} catch (error) {
			console.error('Error generating insight:', error);
		} finally {
			isGeneratingInsight = false;
		}
	}

	async function loadAllData() {
		if (!userId) {
			console.error('No userId available, cannot load data');
			isLoading = false;
			return;
		}
		
		isLoading = true;
		errorMessage = '';
		
		try {
			await Promise.all([
				fetchPredictions(),
				fetchTrends(),
				fetchRecommendations()
			]);
		} catch (error) {
			console.error('Error loading data:', error);
			errorMessage = 'Failed to load AI insights. Please try refreshing the page.';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		// Check if user is logged in from sessionStorage
		const userData = sessionStorage.getItem('user');
		if (userData) {
			try {
				const parsedUser = JSON.parse(userData);
				setUser(parsedUser);
				currentUser = parsedUser;
				userId = parsedUser.user_id;
				
				// Check if user is approved
				if (parsedUser.status !== 'approved') {
					isApproved = false;
					isLoading = false;
					return;
				}
				
				loadAllData();
			} catch (e) {
				console.error('Failed to parse user data:', e);
				goto('/');
			}
		} else {
			// Redirect to login if no user data
			goto('/');
		}
	});
</script>

<svelte:head>
	<title>AI Insights - CarbonTrack</title>
</svelte:head>

{#if !isApproved && currentUser}
	<!-- Show Approval Pending Screen -->
	<ApprovalPending userStatus={currentUser.status} userName={currentUser.name} />
{:else}
<div class="min-h-screen bg-gray-50">
	<!-- Top Navigation -->
	<Navbar {toggleSidebar} />

	<!-- Sidebar -->
	<Sidebar {sidebarExpanded} currentPage="ai-insights" />

	<!-- Main Content -->
	<div class="lg:ml-64 pt-16">
		<div class="p-6 space-y-8">
			<!-- Header Section with AI Glow Effect -->
			<div class="text-center mb-8">
				<div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full mb-6 relative">
					<div class="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full animate-pulse opacity-75"></div>
					<Brain class="w-10 h-10 text-white relative z-10" />
				</div>
				<h1 class="text-4xl font-bold text-gray-900 mb-4">AI Insights</h1>
				<p class="text-xl text-gray-600 max-w-2xl mx-auto">Predictive analytics for a cleaner tomorrow</p>
			</div>

			{#if isLoading}
				<div class="flex items-center justify-center py-20">
					<div class="text-center">
						<RefreshCw class="w-12 h-12 text-cyan-500 animate-spin mx-auto mb-4" />
						<p class="text-gray-600">Loading AI insights...</p>
					</div>
				</div>
			{:else if errorMessage}
				<div class="flex items-center justify-center py-20">
					<div class="text-center max-w-md">
						<AlertTriangle class="w-16 h-16 text-orange-500 mx-auto mb-4" />
						<h3 class="text-xl font-semibold text-gray-900 mb-2">Unable to Load Data</h3>
						<p class="text-gray-600 mb-4">{errorMessage}</p>
						<button 
							on:click={loadAllData}
							class="bg-cyan-500 hover:bg-cyan-600 text-white px-6 py-3 rounded-lg transition-colors font-semibold"
						>
							Retry
						</button>
					</div>
				</div>
			{:else if !userId}
				<div class="flex items-center justify-center py-20">
					<div class="text-center max-w-md">
						<Brain class="w-16 h-16 text-gray-400 mx-auto mb-4" />
						<h3 class="text-xl font-semibold text-gray-900 mb-2">No User Data</h3>
						<p class="text-gray-600">Please ensure you are logged in to view AI insights.</p>
					</div>
				</div>
			{:else}
				<!-- Key Predictions Summary - 3 Cards -->
				<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
				<!-- Card 1: Next Month's Carbon Emissions Projection -->
				<div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-300">
					<div class="flex items-center justify-between mb-4">
						<div class="p-3 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg">
							<Leaf class="w-6 h-6 text-white" />
						</div>
						<div class="flex items-center space-x-1 text-sm">
							{#if keyPredictions.nextMonthEmissions.trend === 'down'}
								<ArrowDown class="w-4 h-4 text-green-500" />
								<span class="text-green-600 font-medium">{Math.abs(keyPredictions.nextMonthEmissions.change).toFixed(1)}%</span>
							{:else}
								<ArrowUp class="w-4 h-4 text-red-500" />
								<span class="text-red-600 font-medium">{Math.abs(keyPredictions.nextMonthEmissions.change).toFixed(1)}%</span>
							{/if}
						</div>
					</div>
					<h3 class="text-lg font-semibold text-gray-900 mb-2">Carbon Emissions</h3>
					<p class="text-3xl font-bold text-gray-900 mb-1">{keyPredictions.nextMonthEmissions.value.toLocaleString()}</p>
					<p class="text-sm text-gray-500">kg CO₂ next month</p>
				</div>

				<!-- Card 2: Next Month's Energy Consumption Projection -->
				<div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-300">
					<div class="flex items-center justify-between mb-4">
						<div class="p-3 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-lg">
							<Zap class="w-6 h-6 text-white" />
						</div>
						<div class="flex items-center space-x-1 text-sm">
							{#if keyPredictions.nextMonthEnergy.trend === 'down'}
								<ArrowDown class="w-4 h-4 text-green-500" />
								<span class="text-green-600 font-medium">{Math.abs(keyPredictions.nextMonthEnergy.change).toFixed(1)}%</span>
							{:else}
								<ArrowUp class="w-4 h-4 text-red-500" />
								<span class="text-red-600 font-medium">{Math.abs(keyPredictions.nextMonthEnergy.change).toFixed(1)}%</span>
							{/if}
						</div>
					</div>
					<h3 class="text-lg font-semibold text-gray-900 mb-2">Energy Consumption</h3>
					<p class="text-3xl font-bold text-gray-900 mb-1">{keyPredictions.nextMonthEnergy.value.toLocaleString()}</p>
					<p class="text-sm text-gray-500">kWh next month</p>
				</div>

				<!-- Card 3: Top Risk Sources -->
				<div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-300">
					<div class="flex items-center justify-between mb-4">
						<div class="p-3 bg-gradient-to-r from-red-500 to-pink-600 rounded-lg">
							<AlertTriangle class="w-6 h-6 text-white" />
						</div>
					</div>
					<h3 class="text-lg font-semibold text-gray-900 mb-2">Top Risk Sources</h3>
					<div class="space-y-2">
						{#each keyPredictions.topRiskSources as source, i}
							<div class="flex items-center justify-between">
								<span class="text-gray-700">{i + 1}. {source}</span>
								<div class="w-2 h-2 bg-gradient-to-r from-red-500 to-pink-500 rounded-full"></div>
							</div>
						{/each}
					</div>
				</div>
			</div>

			<!-- Two Graphs Side by Side -->
<div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
	<!-- Carbon Emissions Chart -->
	<div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-300">
		<div class="flex items-center justify-between mb-6">
			<div class="flex items-center space-x-3">
				<div class="p-2 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg">
					<Leaf class="w-5 h-5 text-white" />
				</div>
				<div>
					<h3 class="text-lg font-semibold text-gray-900">Carbon Emissions Trend</h3>
					<p class="text-sm text-gray-500">Actual vs Predicted (kg CO₂)</p>
				</div>
			</div>
			<Activity class="w-5 h-5 text-gray-400" />
		</div>

		<!-- Chart Area -->
		<div class="h-64 flex items-end justify-between space-x-2 px-2">
			{#each emissionsTrendData as point}
				<div class="flex-1 flex flex-col items-center space-y-2">
					<!-- Bars Container -->
					<div class="w-full flex items-end justify-center space-x-1 h-48">
						<!-- Actual Bar -->
						{#if point.actual !== null}
							<div 
								class="w-full bg-gradient-to-t from-green-500 to-emerald-400 rounded-t-md transition-all duration-500 hover:from-green-600 hover:to-emerald-500 relative group"
								style="height: {getBarHeight(point.actual, emissionsMaxValue)}"
							>
								<!-- Tooltip -->
								<div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
									Actual: {point.actual.toLocaleString()} kg
								</div>
							</div>
						{:else}
							<div class="w-full bg-gray-100 rounded-t-md" style="height: 3%"></div>
						{/if}
						
					<!-- Predicted Bar -->
					{#if point.predicted !== null}
						<div 
							class="w-full bg-gradient-to-t from-cyan-500 to-blue-400 rounded-t-md transition-all duration-500 hover:from-cyan-600 hover:to-blue-500 relative group"
							style="height: {getBarHeight(point.predicted, emissionsMaxValue)}"
						>
							<!-- Tooltip -->
							<div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
								Predicted: {point.predicted.toLocaleString()} kg
							</div>
						</div>
					{:else}
						<div class="w-full bg-gray-100 rounded-t-md" style="height: 3%"></div>
					{/if}
					</div>
					
					<!-- Month Label -->
					<span class="text-xs font-medium text-gray-600">{point.month}</span>
				</div>
			{/each}
		</div>

		<!-- Legend -->
		<div class="flex items-center justify-center space-x-6 mt-6 pt-4 border-t border-gray-100">
			<div class="flex items-center space-x-2">
				<div class="w-4 h-4 bg-gradient-to-r from-green-500 to-emerald-400 rounded"></div>
				<span class="text-sm text-gray-600">Actual</span>
			</div>
			<div class="flex items-center space-x-2">
				<div class="w-4 h-4 bg-gradient-to-r from-cyan-500 to-blue-400 rounded border-2 border-dashed border-cyan-300"></div>
				<span class="text-sm text-gray-600">Predicted</span>
			</div>
		</div>
	</div>

	<!-- Energy Consumption Chart -->
	<div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-300">
		<div class="flex items-center justify-between mb-6">
			<div class="flex items-center space-x-3">
				<div class="p-2 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-lg">
					<Zap class="w-5 h-5 text-white" />
				</div>
				<div>
					<h3 class="text-lg font-semibold text-gray-900">Energy Consumption Trend</h3>
					<p class="text-sm text-gray-500">Actual vs Predicted (kWh)</p>
				</div>
			</div>
			<Activity class="w-5 h-5 text-gray-400" />
		</div>

		<!-- Chart Area -->
		<div class="h-64 flex items-end justify-between space-x-2 px-2">
			{#each energyTrendData as point}
				<div class="flex-1 flex flex-col items-center space-y-2">
					<!-- Bars Container -->
					<div class="w-full flex items-end justify-center space-x-1 h-48">
						<!-- Actual Bar -->
						{#if point.actual !== null}
							<div 
								class="w-full bg-gradient-to-t from-yellow-500 to-amber-400 rounded-t-md transition-all duration-500 hover:from-yellow-600 hover:to-amber-500 relative group"
								style="height: {getBarHeight(point.actual, energyMaxValue)}"
							>
								<!-- Tooltip -->
								<div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
									Actual: {point.actual.toLocaleString()} kWh
								</div>
							</div>
						{:else}
							<div class="w-full bg-gray-100 rounded-t-md" style="height: 3%"></div>
						{/if}
						
					<!-- Predicted Bar -->
					{#if point.predicted !== null}
						<div 
							class="w-full bg-gradient-to-t from-purple-500 to-pink-400 rounded-t-md transition-all duration-500 hover:from-purple-600 hover:to-pink-500 relative group"
							style="height: {getBarHeight(point.predicted, energyMaxValue)}"
						>
							<!-- Tooltip -->
							<div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
								Predicted: {point.predicted.toLocaleString()} kWh
							</div>
						</div>
					{:else}
						<div class="w-full bg-gray-100 rounded-t-md" style="height: 3%"></div>
					{/if}
					</div>
					
					<!-- Month Label -->
					<span class="text-xs font-medium text-gray-600">{point.month}</span>
				</div>
			{/each}
		</div>

		<!-- Legend -->
		<div class="flex items-center justify-center space-x-6 mt-6 pt-4 border-t border-gray-100">
			<div class="flex items-center space-x-2">
				<div class="w-4 h-4 bg-gradient-to-r from-yellow-500 to-amber-400 rounded"></div>
				<span class="text-sm text-gray-600">Actual</span>
			</div>
			<div class="flex items-center space-x-2">
				<div class="w-4 h-4 bg-gradient-to-r from-purple-500 to-pink-400 rounded border-2 border-dashed border-purple-300"></div>
				<span class="text-sm text-gray-600">Predicted</span>
			</div>
		</div>
	</div>
</div>

			<!-- AI Insights Feed -->
			<div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
				<div class="p-6 border-b border-gray-200">
					<div class="flex items-center justify-between">
						<div class="flex items-center space-x-3">
							<Bot class="w-6 h-6 text-purple-600" />
							<h3 class="text-xl font-semibold text-gray-900">AI Insights Feed</h3>
						</div>
						<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-50 text-purple-700 border border-purple-200">
							Live Updates
						</span>
					</div>
				</div>

				<div class="divide-y divide-gray-100">
					{#each aiInsights as insight}
						<div class="p-6 hover:bg-gray-50 transition-colors border-l-4 {getSeverityColor(insight.severity)}">
							<div class="flex items-start space-x-4">
								<div class="p-2 bg-white rounded-lg shadow-sm border">
									<svelte:component this={insight.icon} class="w-5 h-5 {getIconColor(insight.severity)}" />
								</div>
								
								<div class="flex-1">
									<div class="flex items-start justify-between">
										<div>
											<h4 class="text-lg font-semibold text-gray-900 mb-1">{insight.title}</h4>
											<p class="text-gray-700 leading-relaxed mb-3">{insight.message}</p>
											
											<div class="flex items-center space-x-4 text-sm text-gray-500">
												<div class="flex items-center space-x-1">
													<Target class="w-4 h-4" />
													<span>{insight.confidence}% confidence</span>
												</div>
												<div class="flex items-center space-x-1">
													<Clock class="w-4 h-4" />
													<span>{insight.timestamp}</span>
												</div>
											</div>
										</div>
										
										<button class="p-2 text-gray-400 hover:text-gray-600 transition-colors">
											<ArrowRight class="w-5 h-5" />
										</button>
									</div>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
			{/if}
		</div>
	</div>
</div>
{/if}

<style>
	@keyframes glow {
		0%, 100% { box-shadow: 0 0 20px rgba(34, 197, 94, 0.3); }
		50% { box-shadow: 0 0 30px rgba(34, 197, 94, 0.6); }
	}
	
	.animate-glow {
		animation: glow 2s ease-in-out infinite;
	}

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