<script>
	import { onMount } from 'svelte';
	import Navbar from '$lib/widgets/Navbar.svelte';
	import Sidebar from '$lib/widgets/Sidebar.svelte';
	import { Leaf, CheckCircle, Award, Plus, Edit2, Trash2 } from 'lucide-svelte';

	let sidebarExpanded = false;
	function toggleSidebar() { sidebarExpanded = !sidebarExpanded; }

	// Sample goal progress
	let goals = [
		{ id: 1, title: 'Energy Efficiency', progress: 65, target: '70% by Dec' },
		{ id: 2, title: 'Carbon Neutrality', progress: 40, target: 'Net-zero by 2030' }
	];

	let achievements = [
		{ id: 1, title: 'Reduced 2.5 tons CO₂', subtitle: 'This month', icon: Award },
		{ id: 2, title: 'Public transport 15x', subtitle: 'This month', icon: Leaf },
		{ id: 3, title: 'Solar installed', subtitle: 'Completed', icon: CheckCircle }
	];

	let newGoalTitle = '';

	function addGoal() {
		if (!newGoalTitle.trim()) return;
		const id = goals.length ? Math.max(...goals.map(g => g.id)) + 1 : 1;
		goals = [{ id, title: newGoalTitle, progress: 0, target: 'Set target' }, ...goals];
		newGoalTitle = '';
	}

	function removeGoal(id) { goals = goals.filter(g => g.id !== id); }

	function updateProgress(id, delta) {
		goals = goals.map(g => g.id === id ? { ...g, progress: Math.min(100, Math.max(0, g.progress + delta)) } : g);
	}
</script>

<svelte:head>
	<title>Sustainability Goals - CarbonTrack</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<Navbar {toggleSidebar} />
	<Sidebar {sidebarExpanded} currentPage="sustainability" />

	<div class="lg:ml-64 pt-16 p-6 space-y-8">
		<!-- Header -->
		<div class="text-center">
			<h1 class="text-4xl font-bold text-gray-900">Sustainability Goals</h1>
			<p class="text-lg text-gray-600">Your path to a greener future</p>
		</div>

		<!-- Progress Rings & Bars -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			<!-- Circular ring using SVG -->
			{#each goals as goal}
				<div class="bg-white border border-gray-200 rounded-xl p-6 flex flex-col items-center space-y-4 hover:shadow-md transition-all">
					<div class="relative w-36 h-36">
						<svg class="w-36 h-36 transform -rotate-90" viewBox="0 0 36 36">
							<path class="text-gray-200" stroke-width="3" stroke="currentColor" fill="none" d="M18 2.0845a15.9155 15.9155 0 1 1 0 31.831" />
							<path stroke-width="3" stroke-linecap="round" stroke="currentColor" fill="none"
								style="stroke-dasharray: {goal.progress} 100;"
								d="M18 2.0845a15.9155 15.9155 0 1 1 0 31.831" />
						</svg>
						<div class="absolute inset-0 flex flex-col items-center justify-center">
							<p class="text-sm text-gray-500">{goal.title}</p>
							<p class="text-2xl font-bold text-gray-900">{goal.progress}%</p>
							<p class="text-xs text-gray-500">{goal.target}</p>
						</div>
					</div>

					<div class="flex space-x-2">
						<button on:click={() => updateProgress(goal.id, 5)} class="px-3 py-1 bg-green-600 text-white rounded-md">+5%</button>
						<button on:click={() => updateProgress(goal.id, -5)} class="px-3 py-1 bg-gray-100 text-gray-700 rounded-md">-5%</button>
						<button on:click={() => removeGoal(goal.id)} class="px-3 py-1 bg-red-50 text-red-600 rounded-md">Remove</button>
					</div>
				</div>
			{/each}
		</div>

		<!-- Achievements -->
		<div>
			<h2 class="text-2xl font-semibold text-gray-900 mb-4">Achievements</h2>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
				{#each achievements as a}
					<div class="bg-white border border-gray-200 rounded-xl p-6 flex items-start space-x-4 hover:shadow-md transition-all">
						<div class="p-3 bg-green-50 rounded-lg">
							<svelte:component this={a.icon} class="w-6 h-6 text-green-600" />
						</div>
						<div>
							<p class="text-lg font-semibold text-gray-900">{a.title}</p>
							<p class="text-sm text-gray-500">{a.subtitle}</p>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Goal Management -->
		<div class="bg-white border border-gray-200 rounded-xl p-6">
			<h2 class="text-2xl font-semibold text-gray-900 mb-4">Manage Goals</h2>
			<div class="flex items-center space-x-3">
				<input bind:value={newGoalTitle} placeholder="New goal title" class="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500" />
				<button on:click={addGoal} class="px-4 py-2 bg-green-600 text-white rounded-md flex items-center space-x-2">
					<Plus class="w-4 h-4" />
					<span>Add Goal</span>
				</button>
			</div>
		</div>

		<!-- Motivational Banner -->
		<div class="mt-6 bg-gradient-to-r from-green-50 to-teal-50 border border-green-200 rounded-xl p-6 text-center">
			<p class="text-lg text-gray-700">"Every small step counts 🌱" — Keep going, you're making a difference.</p>
		</div>
	</div>
</div>

<style>
	/* Make the circular progress stroke colors */
	svg path[style] { stroke: #16a34a; }
</style>