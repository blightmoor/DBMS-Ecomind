<script>
	import { goto } from '$app/navigation';
	import { setUser } from '../../stores';
	import { API_BASE_URL } from '$lib/config';
	import { Leaf, Eye, EyeOff, Mail, Lock, Github, Linkedin } from 'lucide-svelte';

	let username = '';
	let password = '';
	let errorMessage = '';
	let isLoading = false;
	let showPassword = false;
	let rememberMe = false;

	async function handleSubmit() {
		if (!username || !password) {
			errorMessage = 'Please enter both username and password';
			return;
		}

		isLoading = true;
		errorMessage = '';

		try {
			const response = await fetch(`${API_BASE_URL}/login`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					username: username,
					password: password
				})
			});

			const data = await response.json();

			if (data.success) {
				// Store user data using the store
				setUser(data.user_data);
				// Redirect to home page
				goto('/home');
			} else {
				errorMessage = data.message || 'Login failed';
			}
		} catch (error) {
			console.error('Login error:', error);
			errorMessage = 'Unable to connect to server. Please try again.';
		} finally {
			isLoading = false;
		}
	}

	function togglePasswordVisibility() {
		showPassword = !showPassword;
	}

	function goToOverview() {
		goto('/');
	}
</script>

<svelte:head>
	<title>Login - EcoMind</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-white via-green-50 to-teal-50 relative overflow-hidden">
	<!-- Navigation Bar -->
	<nav class="relative z-20 w-full h-16 bg-white/80 backdrop-blur-md border-b border-gray-200/50 flex items-center justify-between px-6 lg:px-8 shadow-sm">
		<!-- Logo - Clickable to go home -->
		<button 
			on:click={() => goto('/')}
			class="flex items-center gap-3 hover:opacity-80 transition-opacity"
		>
			<div class="w-10 h-10 bg-gradient-to-br from-green-600 to-teal-600 rounded-xl flex items-center justify-center shadow-md">
				<Leaf class="w-6 h-6 text-white" />
			</div>
			<span class="text-xl font-bold bg-gradient-to-r from-green-700 to-teal-700 bg-clip-text text-transparent">EcoMind</span>
		</button>
		
		<!-- Right side placeholder for future nav items if needed -->
		<div></div>
	</nav>

	<!-- Floating Background Elements -->
	<div class="absolute inset-0 overflow-hidden pointer-events-none">
		<div class="absolute top-32 left-16 w-40 h-40 bg-green-100 rounded-full opacity-20 animate-pulse"></div>
		<div class="absolute top-20 right-32 w-24 h-24 bg-teal-100 rounded-full opacity-30 animate-pulse delay-1000"></div>
		<div class="absolute bottom-32 left-32 w-28 h-28 bg-green-200 rounded-full opacity-25 animate-pulse delay-2000"></div>
		<div class="absolute bottom-20 right-20 w-20 h-20 bg-teal-200 rounded-full opacity-35 animate-pulse delay-3000"></div>
	</div>

	<div class="relative z-10 grid grid-cols-1 lg:grid-cols-2" style="min-height: calc(100vh - 4rem);">
		<!-- Left Side - Hero Content -->
		<div class="hidden lg:flex flex-col justify-center items-center p-12 bg-gradient-to-br from-green-100 to-teal-100 relative">
			<div class="max-w-lg text-center space-y-8">
				<!-- Logo -->
				<div class="flex items-center justify-center gap-3 mb-12">
					<div class="w-14 h-14 bg-gradient-to-br from-green-600 to-teal-600 rounded-2xl flex items-center justify-center shadow-xl">
						<Leaf class="w-8 h-8 text-white" />
					</div>
					<span class="text-3xl font-bold bg-gradient-to-r from-green-700 to-teal-700 bg-clip-text text-transparent">EcoMind</span>
				</div>

				<!-- Modern Illustration -->
				<div class="relative mb-12">
					<div class="w-80 h-80 mx-auto relative">
						<!-- Main Circle -->
						<div class="absolute inset-0 bg-gradient-to-br from-green-200 to-teal-200 rounded-full shadow-2xl"></div>
						
						<!-- Inner Elements -->
						<div class="absolute inset-8 bg-white rounded-full shadow-inner flex items-center justify-center">
							<!-- Center Icon -->
							<div class="w-24 h-24 bg-gradient-to-br from-green-500 to-teal-500 rounded-2xl flex items-center justify-center shadow-xl transform rotate-12">
								<Leaf class="w-12 h-12 text-white" />
							</div>
							
							<!-- Floating Data Points -->
							<div class="absolute top-16 left-16 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
							<div class="absolute top-24 right-20 w-2 h-2 bg-teal-400 rounded-full animate-pulse delay-300"></div>
							<div class="absolute bottom-20 left-24 w-2 h-2 bg-green-500 rounded-full animate-pulse delay-700"></div>
							<div class="absolute bottom-16 right-16 w-3 h-3 bg-teal-500 rounded-full animate-pulse delay-1000"></div>
						</div>

						<!-- Orbiting Elements -->
						<div class="absolute top-4 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-green-400 rounded-lg shadow-lg animate-pulse"></div>
						<div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-teal-400 rounded-lg shadow-lg animate-pulse delay-500"></div>
						<div class="absolute left-4 top-1/2 transform -translate-y-1/2 w-3 h-3 bg-green-500 rounded-full shadow-lg animate-pulse delay-1000"></div>
						<div class="absolute right-4 top-1/2 transform -translate-y-1/2 w-3 h-3 bg-teal-500 rounded-full shadow-lg animate-pulse delay-1500"></div>
					</div>
				</div>

				<!-- Slogan -->
				<div class="space-y-6">
					<h2 class="text-4xl font-bold text-green-800 leading-tight">
						Track. Predict. Reduce.
					</h2>
					<p class="text-xl text-green-700 font-semibold">Sustain the Future.</p>
					<p class="text-lg text-green-600 leading-relaxed max-w-md mx-auto">
						Harness AI-powered insights to monitor and optimize your environmental impact for a sustainable tomorrow.
					</p>
				</div>
			</div>
		</div>

		<!-- Right Side - Login Form -->
		<div class="flex flex-col justify-center items-center p-8 lg:p-12 bg-white">

			<div class="w-full max-w-lg">
				<!-- Login Card -->
				<div class="bg-white rounded-3xl shadow-2xl border border-gray-100 p-10">
					<div class="text-center mb-10">
						<h1 class="text-4xl font-bold text-gray-900 mb-4">Welcome Back</h1>
						<p class="text-gray-600 text-lg">Continue your sustainability journey</p>
					</div>

					<form on:submit|preventDefault={handleSubmit} class="space-y-8">
						{#if errorMessage}
							<div class="bg-red-50 border-l-4 border-red-400 text-red-700 px-6 py-4 rounded-r-xl text-sm">
								<div class="flex">
									<div class="ml-3">
										<p>{errorMessage}</p>
									</div>
								</div>
							</div>
						{/if}
						
						<div class="space-y-6">
							<div>
								<label for="username" class="flex items-center gap-3 text-base font-semibold text-gray-700 mb-3">
									<Mail class="w-5 h-5 text-green-600" />
									Email or Username
								</label>
								<input 
									type="text" 
									id="username" 
									bind:value={username} 
									placeholder="Enter your email or username"
									required
									disabled={isLoading}
									class="w-full px-6 py-4 text-lg border border-gray-200 rounded-2xl focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200 disabled:bg-gray-50 disabled:cursor-not-allowed shadow-sm hover:shadow-lg"
								/>
							</div>
							
							<div>
								<label for="password" class="flex items-center gap-3 text-base font-semibold text-gray-700 mb-3">
									<Lock class="w-5 h-5 text-teal-600" />
									Password
								</label>
								<div class="relative">
									<input 
										type={showPassword ? "text" : "password"}
										id="password" 
										bind:value={password} 
										placeholder="Enter your password"
										required
										disabled={isLoading}
										class="w-full px-6 py-4 pr-14 text-lg border border-gray-200 rounded-2xl focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200 disabled:bg-gray-50 disabled:cursor-not-allowed shadow-sm hover:shadow-lg"
									/>
									<button
										type="button"
										on:click={togglePasswordVisibility}
										class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-green-600 transition-colors p-1"
										disabled={isLoading}
									>
										{#if showPassword}
											<EyeOff class="w-6 h-6" />
										{:else}
											<Eye class="w-6 h-6" />
										{/if}
									</button>
								</div>
							</div>
						</div>

						<!-- Remember Me & Forgot Password -->
						<div class="flex items-center justify-between pt-2">
							<label class="flex items-center">
								<input 
									type="checkbox" 
									bind:checked={rememberMe}
									class="w-5 h-5 rounded border-gray-300 text-green-600 focus:ring-green-500 focus:ring-2"
								/>
								<span class="ml-3 text-base text-gray-600">Remember me</span>
							</label>
							<a href="#" class="text-base text-green-600 hover:text-teal-600 font-semibold hover:underline transition-colors">
								Forgot password?
							</a>
						</div>
						
						<button 
							type="submit" 
							disabled={isLoading}
							class="w-full bg-gradient-to-r from-green-600 to-teal-600 text-white py-5 px-8 rounded-2xl text-lg font-bold hover:from-green-700 hover:to-teal-700 focus:ring-4 focus:ring-green-200 transition-all duration-200 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed flex items-center justify-center gap-3 shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
						>
							{#if isLoading}
								<div class="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
								Signing in...
							{:else}
								Login to EcoMind
							{/if}
						</button>

						<!-- Divider -->
						<div class="relative my-8">
							<div class="absolute inset-0 flex items-center">
								<div class="w-full border-t border-gray-200"></div>
							</div>
							<div class="relative flex justify-center text-base">
								<span class="px-4 bg-white text-gray-500 font-medium">OR</span>
							</div>
						</div>

						<!-- Social Login Buttons -->
						<div class="grid grid-cols-2 gap-4">
							<button 
								type="button"
								class="flex items-center justify-center gap-3 px-6 py-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-all duration-200 shadow-sm hover:shadow-lg transform hover:-translate-y-0.5"
							>
								<svg class="w-6 h-6" viewBox="0 0 24 24">
									<path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
									<path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
									<path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
									<path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
								</svg>
								<span class="text-base font-semibold text-gray-700">Google</span>
							</button>
							<button 
								type="button"
								class="flex items-center justify-center gap-3 px-6 py-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-all duration-200 shadow-sm hover:shadow-lg transform hover:-translate-y-0.5"
							>
								<Linkedin class="w-6 h-6 text-blue-600" />
								<span class="text-base font-semibold text-gray-700">LinkedIn</span>
							</button>
						</div>
					</form>

					<div class="mt-10 text-center">
						<p class="text-gray-600 text-lg">
							Don't have an account? 
							<a href="/signup" class="text-green-600 hover:text-teal-600 font-bold hover:underline transition-colors">
								Sign up here
							</a>
						</p>
					</div>
				</div>

				<!-- Bottom Text -->
				<div class="text-center mt-8">
					<p class="text-gray-500">
						Secure login • Privacy protected • AI-powered sustainability
					</p>
				</div>
			</div>
		</div>
	</div>
</div>
