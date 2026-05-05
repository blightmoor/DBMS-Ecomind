<script>
	import { onMount } from 'svelte';
	import Navbar from '$lib/widgets/Navbar.svelte';
	import Sidebar from '$lib/widgets/Sidebar.svelte';
	import { 
		Leaf, 
		Bell, 
		Settings, 
		User, 
		Menu, 
		X,
		BarChart3,
		TrendingUp,
		Filter,
		Zap,
		Car,
		Home,
		Recycle,
		Wind,
		Sun,
		Trees,
		Droplets,
		Shield,
		CheckCircle,
		Clock,
		Target,
		Award,
		ArrowRight
	} from 'lucide-svelte';

	let sidebarExpanded = false;
	
	function toggleSidebar() {
		sidebarExpanded = !sidebarExpanded;
	}
	let selectedCategory = 'all';
	let implementedCount = 7;
	let totalRecommendations = 12;

	// Sample recommendations data
	let recommendations = [
		{
			id: 1,
			title: 'Switch to Renewable Energy',
			description: 'Transition to solar or wind power to significantly reduce your carbon footprint from electricity usage.',
			category: 'Energy',
			impact: 85,
			co2Reduction: '1,200 kg/year',
			difficulty: 'Medium',
			timeToImplement: '2-3 months',
			icon: Sun,
			status: 'recommended',
			color: 'from-yellow-500 to-orange-500'
		},
		{
			id: 2,
			title: 'Optimize Vehicle Routes',
			description: 'Use AI-powered route optimization to reduce fuel consumption and emissions from transportation.',
			category: 'Transport',
			impact: 65,
			co2Reduction: '450 kg/year',
			difficulty: 'Easy',
			timeToImplement: '1 week',
			icon: Car,
			status: 'implemented',
			color: 'from-blue-500 to-cyan-500'
		},
		{
			id: 3,
			title: 'Implement Smart Thermostat',
			description: 'Install programmable thermostats to optimize heating and cooling energy consumption.',
			category: 'Energy',
			impact: 45,
			co2Reduction: '320 kg/year',
			difficulty: 'Easy',
			timeToImplement: '2-3 days',
			icon: Home,
			status: 'in-progress',
			color: 'from-green-500 to-emerald-500'
		},
		{
			id: 4,
			title: 'Carbon Offset Programs',
			description: 'Invest in verified carbon offset projects like reforestation and renewable energy.',
			category: 'Lifestyle',
			impact: 70,
			co2Reduction: '500 kg/year',
			difficulty: 'Easy',
			timeToImplement: '1 day',
			icon: Trees,
			status: 'recommended',
			color: 'from-green-600 to-teal-600'
		},
		{
			id: 5,
			title: 'Water Conservation System',
			description: 'Install rainwater harvesting and greywater recycling systems to reduce water-related emissions.',
			category: 'Lifestyle',
			impact: 35,
			co2Reduction: '180 kg/year',
			difficulty: 'Hard',
			timeToImplement: '1-2 months',
			icon: Droplets,
			status: 'recommended',
			color: 'from-blue-400 to-blue-600'
		},
		{
			id: 6,
			title: 'Waste Reduction Program',
			description: 'Implement comprehensive recycling and composting to minimize waste-related emissions.',
			category: 'Lifestyle',
			impact: 40,
			co2Reduction: '250 kg/year',
			difficulty: 'Medium',
			timeToImplement: '2-4 weeks',
			icon: Recycle,
			status: 'implemented',
			color: 'from-purple-500 to-pink-500'
		}
	];

	let categories = ['all', 'Energy', 'Transport', 'Lifestyle'];

	$: filteredRecommendations = selectedCategory === 'all' 
		? recommendations 
		: recommendations.filter(rec => rec.category === selectedCategory);

	$: progressPercentage = (implementedCount / totalRecommendations) * 100;

	function getStatusColor(status) {
		switch(status) {
			case 'implemented': return 'bg-green-50 text-green-700 border-green-200';
			case 'in-progress': return 'bg-yellow-50 text-yellow-700 border-yellow-200';
			default: return 'bg-gray-50 text-gray-700 border-gray-200';
		}
	}

	function getStatusIcon(status) {
		switch(status) {
			case 'implemented': return CheckCircle;
			case 'in-progress': return Clock;
			default: return Target;
		}
	}

	function getDifficultyColor(difficulty) {
		switch(difficulty) {
			case 'Easy': return 'text-green-600';
			case 'Medium': return 'text-yellow-600';
			case 'Hard': return 'text-red-600';
			default: return 'text-gray-600';
		}
	}
</script>

<svelte:head>
	<title>Recommendations - CarbonTrack</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Top Navigation -->
	<Navbar {toggleSidebar} />

	<!-- Sidebar -->
	<Sidebar {sidebarExpanded} currentPage="recommendations" />

	<!-- Main Content -->
	<div class="lg:ml-64 pt-16">
		<div class="p-6 space-y-6">
			<!-- Header Section -->
			<div class="text-center mb-8">
				<h1 class="text-4xl font-bold text-gray-900 mb-4">Recommendations</h1>
				<p class="text-xl text-gray-600 max-w-2xl mx-auto">AI-powered insights to reduce your emissions and create a more sustainable future</p>
			</div>

			<!-- Progress Tracker -->
			<div class="bg-gradient-to-r from-green-50 to-teal-50 border border-green-200 rounded-xl p-6 mb-8">
				<div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
					<div>
						<h3 class="text-xl font-semibold text-gray-900 mb-2">Your Progress</h3>
						<p class="text-gray-600">You've implemented {implementedCount} out of {totalRecommendations} recommendations</p>
					</div>
					
					<div class="flex items-center space-x-4">
						<div class="flex items-center space-x-2">
							<Award class="w-6 h-6 text-green-600" />
							<span class="text-green-600 font-semibold">{Math.round(progressPercentage)}% Complete</span>
						</div>
						<div class="w-32 h-3 bg-gray-200 rounded-full overflow-hidden">
							<div 
								class="h-full bg-gradient-to-r from-green-500 to-teal-500 rounded-full transition-all duration-500"
								style="width: {progressPercentage}%"
							></div>
						</div>
					</div>
				</div>
			</div>

			<!-- Filters -->
			<div class="flex flex-wrap items-center gap-4 mb-8">
				<div class="flex items-center space-x-2">
					<Filter class="w-5 h-5 text-gray-500" />
					<span class="text-gray-700 font-medium">Filter by category:</span>
				</div>
				
				<div class="flex flex-wrap gap-2">
					{#each categories as category}
						<button 
							on:click={() => selectedCategory = category}
							class={`px-4 py-2 rounded-lg font-medium transition-all ${
								selectedCategory === category 
									? 'bg-green-500 text-white shadow-lg shadow-green-500/25' 
									: 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 hover:text-gray-900'
							}`}
						>
							{category === 'all' ? 'All Categories' : category}
						</button>
					{/each}
				</div>
			</div>

			<!-- Recommendations Grid -->
			<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
				{#each filteredRecommendations as recommendation}
					<div class="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-md hover:border-gray-300 transition-all duration-300 group">
						<!-- Card Header -->
						<div class="p-6 pb-4">
							<div class="flex items-start justify-between mb-4">
								<div class="p-3 rounded-lg bg-gradient-to-br {recommendation.color}">
									<svelte:component this={recommendation.icon} class="w-6 h-6 text-white" />
								</div>
								
								<div class="flex items-center space-x-2">
									<span class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(recommendation.status)}`}>
										<svelte:component this={getStatusIcon(recommendation.status)} class="w-3 h-3 mr-1" />
										{recommendation.status.replace('-', ' ')}
									</span>
								</div>
							</div>

							<h3 class="text-xl font-semibold text-gray-900 mb-2 group-hover:text-green-600 transition-colors">
								{recommendation.title}
							</h3>
							<p class="text-gray-600 text-sm leading-relaxed">
								{recommendation.description}
			</p>
						</div>

						<!-- Card Body -->
						<div class="px-6 pb-4">
							<div class="flex items-center justify-between text-sm mb-4">
								<div class="flex items-center space-x-4">
									<div>
										<p class="text-gray-500">Category</p>
										<p class="text-gray-700 font-medium">{recommendation.category}</p>
									</div>
									<div>
										<p class="text-gray-500">Difficulty</p>
										<p class={`font-medium ${getDifficultyColor(recommendation.difficulty)}`}>
											{recommendation.difficulty}
										</p>
									</div>
								</div>
							</div>

							<!-- Impact Score -->
							<div class="mb-4">
								<div class="flex items-center justify-between text-sm mb-2">
									<span class="text-gray-500">Impact Score</span>
									<span class="text-gray-900 font-semibold">{recommendation.impact}/100</span>
								</div>
								<div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
									<div 
										class="h-full bg-gradient-to-r from-green-500 to-teal-500 rounded-full transition-all duration-500"
										style="width: {recommendation.impact}%"
									></div>
								</div>
							</div>

							<!-- Metrics -->
							<div class="grid grid-cols-2 gap-4 mb-6">
								<div class="text-center p-3 bg-gray-50 rounded-lg">
									<p class="text-2xl font-bold text-green-600">{recommendation.co2Reduction}</p>
									<p class="text-gray-500 text-xs">CO₂ Reduction</p>
								</div>
								<div class="text-center p-3 bg-gray-50 rounded-lg">
									<p class="text-sm font-semibold text-gray-900">{recommendation.timeToImplement}</p>
									<p class="text-gray-500 text-xs">Time to Implement</p>
								</div>
							</div>
						</div>

						<!-- Card Footer -->
						<div class="px-6 pb-6">
							<button class="w-full bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-300 flex items-center justify-center space-x-2 group-hover:shadow-lg group-hover:shadow-green-500/25">
								<span>
									{#if recommendation.status === 'implemented'}
										View Details
									{:else if recommendation.status === 'in-progress'}
										Continue Setup
									{:else}
										Get Started
									{/if}
								</span>
								<ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
							</button>
						</div>
					</div>
				{/each}
			</div>

			<!-- Achievement Section -->
			<div class="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-8 mt-12">
				<div class="text-center">
					<div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mb-4">
						<Shield class="w-8 h-8 text-white" />
					</div>
					<h3 class="text-2xl font-bold text-gray-900 mb-2">Environmental Impact Champion</h3>
					<p class="text-gray-600 mb-4">
						You're making a significant impact! Your implemented recommendations have saved approximately 
						<span class="text-green-600 font-semibold">2,450 kg CO₂</span> this year.
					</p>
					<button class="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300 shadow-lg shadow-purple-500/25">
						Share Your Achievement
					</button>
				</div>
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