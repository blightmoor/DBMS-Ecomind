<script lang="ts">
	import { Clock, AlertCircle, Mail, CheckCircle } from 'lucide-svelte';
	import { goto } from '$app/navigation';
	
	export let userStatus: string = 'pending';
	export let userName: string = '';
	
	function handleLogout() {
		sessionStorage.removeItem('user');
		goto('/');
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 flex items-center justify-center p-6">
	<div class="max-w-2xl w-full">
		<!-- Approval Pending Card -->
		<div class="bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden">
			<!-- Header with Animation -->
			<div class="bg-gradient-to-r from-blue-500 to-indigo-600 p-8 text-center relative overflow-hidden">
				<!-- Animated Background Circles -->
				<div class="absolute top-0 left-0 w-32 h-32 bg-white opacity-10 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
				<div class="absolute bottom-0 right-0 w-40 h-40 bg-white opacity-10 rounded-full translate-x-1/2 translate-y-1/2"></div>
				
				<div class="relative z-10">
					<!-- Icon -->
					<div class="inline-flex items-center justify-center w-20 h-20 bg-white rounded-full mb-4 shadow-lg">
						{#if userStatus === 'pending'}
							<Clock class="w-10 h-10 text-blue-600 animate-pulse" />
						{:else if userStatus === 'rejected'}
							<AlertCircle class="w-10 h-10 text-red-600" />
						{:else}
							<CheckCircle class="w-10 h-10 text-green-600" />
						{/if}
					</div>
					
					<h1 class="text-3xl font-bold text-white mb-2">
						{#if userStatus === 'pending'}
							Approval Pending
						{:else if userStatus === 'rejected'}
							Access Denied
						{:else}
							Account Under Review
						{/if}
					</h1>
					<p class="text-blue-100 text-lg">
						Hi {userName || 'User'}!
					</p>
				</div>
			</div>

			<!-- Content -->
			<div class="p-10 space-y-8">
				{#if userStatus === 'pending'}
					<!-- Pending Status -->
					<div class="text-center space-y-4">
						<p class="text-xl text-gray-700 leading-relaxed">
							Your account is currently <span class="font-semibold text-blue-600">awaiting approval</span> from an administrator.
						</p>
						<p class="text-gray-600">
							This is a standard security measure to ensure the integrity of our platform.
						</p>
					</div>

					<!-- Status Steps -->
					<div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 space-y-4">
						<h3 class="font-semibold text-gray-900 text-lg mb-4">What happens next?</h3>
						
						<div class="space-y-3">
							<div class="flex items-start gap-3">
								<div class="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0 mt-0.5">
									<CheckCircle class="w-5 h-5 text-white" />
								</div>
								<div>
									<p class="font-medium text-gray-900">Registration Complete</p>
									<p class="text-sm text-gray-600">Your account has been successfully created</p>
								</div>
							</div>

							<div class="flex items-start gap-3">
								<div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0 mt-0.5 animate-pulse">
									<Clock class="w-5 h-5 text-white" />
								</div>
								<div>
									<p class="font-medium text-gray-900">Admin Review</p>
									<p class="text-sm text-gray-600">An administrator is reviewing your request</p>
								</div>
							</div>

							<div class="flex items-start gap-3">
								<div class="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center flex-shrink-0 mt-0.5">
									<Mail class="w-5 h-5 text-gray-500" />
								</div>
								<div>
									<p class="font-medium text-gray-900">Email Notification</p>
									<p class="text-sm text-gray-600">You'll receive an email once approved</p>
								</div>
							</div>
						</div>
					</div>

					<!-- Timeline -->
					<div class="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
						<div class="flex items-start gap-3">
							<Clock class="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
							<div>
								<p class="text-sm font-medium text-yellow-900">Expected approval time: 24-48 hours</p>
								<p class="text-xs text-yellow-700 mt-1">Most accounts are reviewed within one business day</p>
							</div>
						</div>
					</div>

				{:else if userStatus === 'rejected'}
					<!-- Rejected Status -->
					<div class="text-center space-y-4">
						<p class="text-xl text-gray-700 leading-relaxed">
							We're sorry, but your account access has been <span class="font-semibold text-red-600">denied</span>.
						</p>
						<p class="text-gray-600">
							If you believe this is a mistake, please contact your administrator.
						</p>
					</div>

					<div class="bg-red-50 border border-red-200 rounded-xl p-4">
						<div class="flex items-start gap-3">
							<AlertCircle class="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
							<div>
								<p class="text-sm font-medium text-red-900">Access Restrictions</p>
								<p class="text-xs text-red-700 mt-1">You cannot access dashboard features at this time</p>
							</div>
						</div>
					</div>
				{/if}

				<!-- Actions -->
				<div class="flex flex-col gap-3 pt-4">
					<button
						on:click={handleLogout}
						class="w-full bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white py-4 px-6 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
					>
						Return to Login
					</button>
					
					{#if userStatus === 'pending'}
						<button
							on:click={() => window.location.reload()}
							class="w-full border-2 border-blue-500 text-blue-600 hover:bg-blue-50 py-4 px-6 rounded-xl font-semibold transition-all duration-200"
						>
							Refresh Status
						</button>
					{/if}
				</div>

				<!-- Help -->
				<div class="text-center pt-6 border-t border-gray-100">
					<p class="text-gray-600 text-sm">
						Need help? Contact your organization administrator
					</p>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}
	
	.animate-pulse {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
</style>
