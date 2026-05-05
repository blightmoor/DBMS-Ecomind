<script lang="ts">
	import { Bell, Settings, User, Leaf } from 'lucide-svelte';
	import { goto } from '$app/navigation';
	import { user, setUser } from '../../stores';
	import { onMount, onDestroy } from 'svelte';
	import { scale } from 'svelte/transition';

	export let toggleSidebar = () => {};

	// Profile dropdown state
	let showProfile: boolean = false;
	let currentUser: any = null;
	let closeTimeout: any = null;

	// Subscribe to user store (safe no-op if store not initialized)
	const unsubscribe: any = user.subscribe((value: any) => {
		currentUser = value || null;
	});

	onMount(() => {
		// try to hydrate from sessionStorage if store is empty
		if (!currentUser) {
			const userData = sessionStorage.getItem('user');
			if (userData) {
				try {
					const parsed = JSON.parse(userData);
					setUser(parsed);
					currentUser = parsed;
				} catch (e) {
					// ignore
				}
			}
		}
	});

	onDestroy(() => {
		if (typeof unsubscribe === 'function') unsubscribe();
		if (closeTimeout) clearTimeout(closeTimeout);
	});

	function goHome() {
		goto('/');
	}

	function logout() {
		// Clear session and store, then navigate to login/home
		sessionStorage.removeItem('user');
		setUser(null as any);
		goto('/');
	}
</script>

<!-- Top Navigation Bar -->
<nav class="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50 shadow-sm">
	<div class="flex items-center justify-between px-6 py-4">
		<!-- Left: Logo and Menu -->
		<div class="flex items-center gap-4">
			<button on:click={toggleSidebar} class="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors" aria-label="Toggle sidebar">
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
				</svg>
			</button>
			
			<div class="flex items-center gap-3 cursor-pointer" role="button" tabindex="0" on:click={goHome} on:keypress={(e) => e.key === 'Enter' && goHome()}>
				<div class="w-8 h-8 bg-gradient-to-br from-green-600 to-teal-600 rounded-lg flex items-center justify-center">
					<Leaf class="w-5 h-5 text-white" />
				</div>
				<div class="flex items-center gap-2">
					<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@600&display=swap" rel="stylesheet">

					<span class="text-xl font-semibold bg-gradient-to-r from-green-700 to-teal-700 bg-clip-text text-transparent" style="font-family:'Quicksand', sans-serif;">
					EcoMind
					</span>
				</div>
			</div>
		</div>

		<!-- Center: Quick Stats -->
		<!-- <div class="hidden md:flex items-center gap-6">
			<div class="text-center">
				<p class="text-sm text-gray-500">Today's Emissions</p>
				<p class="text-lg font-semibold text-green-600">-12.3%</p>
			</div>
			<div class="h-8 w-px bg-gray-200"></div>
			<div class="text-center">
				<p class="text-sm text-gray-500">Monthly Goal</p>
				<p class="text-lg font-semibold text-green-600">78%</p>
			</div>
		</div> -->

		<!-- Right: User Actions -->
		<div class="flex items-center gap-4">
			<Bell class="w-5 h-5 text-gray-500 hover:text-gray-700 cursor-pointer transition-colors" />
			<Settings class="w-5 h-5 text-gray-500 hover:text-gray-700 cursor-pointer transition-colors" />
			
			<div class="relative">
				<button
					type="button"
					class="w-8 h-8 bg-gradient-to-br from-green-500 to-teal-500 rounded-full flex items-center justify-center cursor-pointer"
					on:mouseenter={() => { if (closeTimeout) { clearTimeout(closeTimeout); closeTimeout = null; } showProfile = true; }}
					on:click={() => { showProfile = !showProfile; }}
					on:focus={() => { if (closeTimeout) { clearTimeout(closeTimeout); closeTimeout = null; } showProfile = true; }}
					aria-haspopup="true"
					aria-expanded={showProfile}
					aria-label="Open profile menu"
				>
					<User class="w-5 h-5 text-white" />
				</button>

				{#if showProfile}
					<div
						class="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-100 z-50"
						role="menu"
						aria-label="Profile menu"
						tabindex="0"
						on:mouseenter={() => { if (closeTimeout) { clearTimeout(closeTimeout); closeTimeout = null; } showProfile = true; }}
						on:mouseleave={() => { if (closeTimeout) clearTimeout(closeTimeout); closeTimeout = setTimeout(() => showProfile = false, 160); }}
						on:keydown={(e) => { if (e.key === 'Escape') { showProfile = false; } }}
						in:scale={{ duration: 160, start: 0.95 }}
						out:scale={{ duration: 100, start: 0.95 }}
						style="transform-origin: top right;"
					>
						<div class="p-4">
							<div class="flex items-center gap-3 mb-3">
								<div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
									<User class="w-5 h-5 text-green-600" />
								</div>
								<div>
									<p class="text-sm font-medium text-gray-900">{currentUser?.name ?? 'Guest'}</p>
									<p class="text-xs text-gray-500">{currentUser?.email ?? ''}</p>
								</div>
							</div>

							<div class="text-xs text-gray-500 mb-4">Status: <span class="font-medium text-gray-700">{currentUser?.status ?? 'unknown'}</span></div>

							<div class="flex gap-2">
								<button class="flex-1 px-3 py-2 bg-gray-100 text-sm rounded hover:bg-gray-200" on:click={() => { goHome(); showProfile = false; }}>
									Home
								</button>
								<button class="flex-1 px-3 py-2 bg-red-500 text-sm text-white rounded hover:bg-red-600" on:click={logout}>
									Logout
								</button>
							</div>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</nav>