<script>
	import { onMount } from 'svelte';
	import { user } from '../../stores';
	import { goto } from '$app/navigation';

	let currentUser = null;

	user.subscribe(value => {
		currentUser = value;
	});

	onMount(() => {
		// Redirect if not logged in or not admin
		if (!currentUser) {
			goto('/login');
		} else if (currentUser.role !== 'admin') {
			alert('Access Denied: Admin privileges required');
			goto('/home');
		}
	});
</script>

{#if currentUser && currentUser.role === 'admin'}
	<slot />
{:else}
	<div class="min-h-screen flex items-center justify-center bg-gray-50">
		<div class="text-center">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
			<p class="mt-4 text-gray-600">Verifying access...</p>
		</div>
	</div>
{/if}
