<script lang="ts">
	import { onMount } from 'svelte';
	import { user, type User } from '../../stores';
	import { goto } from '$app/navigation';
	import Navbar from '$lib/widgets/Navbar.svelte';
	import Sidebar from '$lib/widgets/Sidebar.svelte';
	import { API_BASE_URL } from '$lib/config';
	import { 
		Users, 
		Shield, 
		CheckCircle, 
		XCircle, 
		Clock, 
		Trash2,
		Search,
		Filter,
		UserCheck,
		UserX,
		Crown
	} from 'lucide-svelte';

	interface DbUser {
		user_id: number;
		name: string;
		email: string;
		role: string;
		status: string;
		created_at: string;
		org_name: string | null;
	}

	let currentUser: User | null = null;
	let sidebarExpanded = true;
	let allUsers: DbUser[] = [];
	let filteredUsers: DbUser[] = [];
	let loading = true;
	let searchTerm = '';
	let filterStatus = 'all';
	let filterRole = 'all';
	let stats = {
		total: 0,
		pending: 0,
		approved: 0,
		rejected: 0,
		admins: 0
	};

	// Subscribe to user store
	user.subscribe(value => {
		currentUser = value;
		// Redirect if not admin
		if (currentUser && currentUser.role !== 'admin') {
			goto('/home');
		} else if (!currentUser) {
			goto('/login');
		}
	});

	onMount(async () => {
		if (!currentUser) {
			goto('/login');
			return;
		}
		if (currentUser.role !== 'admin') {
			goto('/home');
			return;
		}
		await fetchUsers();
	});

	async function fetchUsers() {
		loading = true;
		try {
			const response = await fetch(`${API_BASE_URL}/admin/users?admin_id=${currentUser?.user_id}`);
			const data = await response.json();
			
			if (data.success) {
				allUsers = data.users;
				calculateStats();
				applyFilters();
			} else {
				console.error('Failed to fetch users');
			}
		} catch (error) {
			console.error('Error fetching users:', error);
		} finally {
			loading = false;
		}
	}

	function calculateStats() {
		stats.total = allUsers.length;
		stats.pending = allUsers.filter(u => u.status === 'pending').length;
		stats.approved = allUsers.filter(u => u.status === 'approved').length;
		stats.rejected = allUsers.filter(u => u.status === 'rejected').length;
		stats.admins = allUsers.filter(u => u.role === 'admin').length;
	}

	function applyFilters() {
		filteredUsers = allUsers.filter(user => {
			// Search filter
			const matchesSearch = searchTerm === '' || 
				user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
				user.email.toLowerCase().includes(searchTerm.toLowerCase());
			
			// Status filter
			const matchesStatus = filterStatus === 'all' || user.status === filterStatus;
			
			// Role filter
			const matchesRole = filterRole === 'all' || user.role === filterRole;
			
			return matchesSearch && matchesStatus && matchesRole;
		});
	}

	async function updateUserStatus(userId: number, newStatus: string) {
		try {
			const response = await fetch(`${API_BASE_URL}/admin/users/status?admin_id=${currentUser?.user_id}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ user_id: userId, status: newStatus })
			});
			
			const data = await response.json();
			if (data.success) {
				await fetchUsers();
			}
		} catch (error) {
			console.error('Error updating status:', error);
		}
	}

	async function updateUserRole(userId: number, newRole: string) {
		try {
			const response = await fetch(`${API_BASE_URL}/admin/users/role?admin_id=${currentUser?.user_id}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ user_id: userId, role: newRole })
			});
			
			const data = await response.json();
			if (data.success) {
				await fetchUsers();
			}
		} catch (error) {
			console.error('Error updating role:', error);
		}
	}

	async function deleteUser(userId: number) {
		if (!confirm('Are you sure you want to delete this user?')) return;
		
		try {
			const response = await fetch(`${API_BASE_URL}/admin/users/${userId}?admin_id=${currentUser?.user_id}`, {
				method: 'DELETE'
			});
			
			const data = await response.json();
			if (data.success) {
				await fetchUsers();
			}
		} catch (error) {
			console.error('Error deleting user:', error);
		}
	}

	function getStatusColor(status: string) {
		switch (status) {
			case 'approved': return 'text-green-600 bg-green-50';
			case 'rejected': return 'text-red-600 bg-red-50';
			case 'pending': return 'text-yellow-600 bg-yellow-50';
			default: return 'text-gray-600 bg-gray-50';
		}
	}

	function getStatusIcon(status: string) {
		switch (status) {
			case 'approved': return CheckCircle;
			case 'rejected': return XCircle;
			case 'pending': return Clock;
			default: return Clock;
		}
	}

	$: {
		searchTerm;
		filterStatus;
		filterRole;
		applyFilters();
	}
</script>

<div class="min-h-screen bg-gray-50">
	<Navbar />
	<Sidebar {sidebarExpanded} currentPage="admin" />

	<!-- Main Content -->
	<main class="ml-0 lg:ml-64 pt-16 min-h-screen">
		<div class="p-6 max-w-7xl mx-auto">
			<!-- Header -->
			<div class="mb-8">
				<div class="flex items-center gap-3 mb-2">
					<div class="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl">
						<Shield class="w-8 h-8 text-white" />
					</div>
					<div>
						<h1 class="text-3xl font-bold text-gray-800">Admin Dashboard</h1>
						<p class="text-gray-600">
							{#if currentUser?.org_id}
								Managing users from your organization
							{:else}
								Managing individual users
							{/if}
						</p>
					</div>
				</div>
			</div>

			<!-- Stats Cards -->
			<div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
				<div class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm text-gray-600 font-medium">Total Users</p>
							<p class="text-3xl font-bold text-gray-800 mt-1">{stats.total}</p>
						</div>
						<Users class="w-8 h-8 text-blue-500" />
					</div>
				</div>

				<div class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm text-gray-600 font-medium">Pending</p>
							<p class="text-3xl font-bold text-yellow-600 mt-1">{stats.pending}</p>
						</div>
						<Clock class="w-8 h-8 text-yellow-500" />
					</div>
				</div>

				<div class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm text-gray-600 font-medium">Approved</p>
							<p class="text-3xl font-bold text-green-600 mt-1">{stats.approved}</p>
						</div>
						<CheckCircle class="w-8 h-8 text-green-500" />
					</div>
				</div>

				<div class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm text-gray-600 font-medium">Rejected</p>
							<p class="text-3xl font-bold text-red-600 mt-1">{stats.rejected}</p>
						</div>
						<XCircle class="w-8 h-8 text-red-500" />
					</div>
				</div>

				<div class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm text-gray-600 font-medium">Admins</p>
							<p class="text-3xl font-bold text-purple-600 mt-1">{stats.admins}</p>
						</div>
						<Crown class="w-8 h-8 text-purple-500" />
					</div>
				</div>
			</div>

			<!-- Filters -->
			<div class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm mb-6">
				<div class="flex flex-col lg:flex-row gap-4">
					<!-- Search -->
					<div class="flex-1">
						<div class="relative">
							<Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
							<input
								type="text"
								bind:value={searchTerm}
								placeholder="Search by name or email..."
								class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
							/>
						</div>
					</div>

					<!-- Status Filter -->
					<div class="flex items-center gap-2">
						<Filter class="w-5 h-5 text-gray-500" />
						<select
							bind:value={filterStatus}
							class="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
						>
							<option value="all">All Status</option>
							<option value="pending">Pending</option>
							<option value="approved">Approved</option>
							<option value="rejected">Rejected</option>
						</select>
					</div>

					<!-- Role Filter -->
					<div>
						<select
							bind:value={filterRole}
							class="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
						>
							<option value="all">All Roles</option>
							<option value="user">Users</option>
							<option value="admin">Admins</option>
						</select>
					</div>
				</div>
			</div>

			<!-- Users Table -->
			<div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead class="bg-gray-50 border-b border-gray-200">
							<tr>
								<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">User</th>
								<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Email</th>
								<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Organization</th>
								<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Role</th>
								<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Status</th>
								<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Joined</th>
								<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Actions</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200">
							{#if loading}
								<tr>
									<td colspan="7" class="px-6 py-12 text-center text-gray-500">
										<div class="flex items-center justify-center gap-2">
											<div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
											Loading users...
										</div>
									</td>
								</tr>
							{:else if filteredUsers.length === 0}
								<tr>
									<td colspan="7" class="px-6 py-12 text-center text-gray-500">
										No users found
									</td>
								</tr>
							{:else}
								{#each filteredUsers as userItem}
									<tr class="hover:bg-gray-50 transition-colors">
										<td class="px-6 py-4">
											<div class="flex items-center gap-3">
												<div class="w-10 h-10 rounded-full bg-gradient-to-br from-green-400 to-teal-500 flex items-center justify-center text-white font-semibold">
													{userItem.name.charAt(0).toUpperCase()}
												</div>
												<div>
													<p class="font-medium text-gray-800">{userItem.name}</p>
												</div>
											</div>
										</td>
										<td class="px-6 py-4 text-gray-600">
											{userItem.email}
										</td>
										<td class="px-6 py-4 text-gray-600">
											{userItem.org_name || 'Individual'}
										</td>
										<td class="px-6 py-4">
											<select
												value={userItem.role}
												on:change={(e) => {
													const target = e.target as HTMLSelectElement;
													updateUserRole(userItem.user_id, target.value);
												}}
												disabled={userItem.user_id === currentUser?.user_id}
												class="px-3 py-1 rounded-lg border border-gray-300 text-sm {userItem.role === 'admin' ? 'bg-purple-50 text-purple-700' : 'bg-blue-50 text-blue-700'}"
											>
												<option value="user">User</option>
												<option value="admin">Admin</option>
											</select>
										</td>
										<td class="px-6 py-4">
											<div class="flex items-center gap-2">
												<span class="px-3 py-1 rounded-full text-xs font-semibold {getStatusColor(userItem.status)}">
													{userItem.status.charAt(0).toUpperCase() + userItem.status.slice(1)}
												</span>
											</div>
										</td>
										<td class="px-6 py-4 text-gray-600 text-sm">
											{new Date(userItem.created_at).toLocaleDateString()}
										</td>
										<td class="px-6 py-4">
											<div class="flex items-center gap-2">
												{#if userItem.status === 'pending'}
													<button
														on:click={() => updateUserStatus(userItem.user_id, 'approved')}
														class="p-2 rounded-lg bg-green-50 text-green-600 hover:bg-green-100 transition-colors"
														title="Approve"
													>
														<UserCheck class="w-4 h-4" />
													</button>
													<button
														on:click={() => updateUserStatus(userItem.user_id, 'rejected')}
														class="p-2 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
														title="Reject"
													>
														<UserX class="w-4 h-4" />
													</button>
												{:else if userItem.status === 'approved'}
													<button
														on:click={() => updateUserStatus(userItem.user_id, 'rejected')}
														class="p-2 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
														title="Reject"
													>
														<UserX class="w-4 h-4" />
													</button>
												{:else}
													<button
														on:click={() => updateUserStatus(userItem.user_id, 'approved')}
														class="p-2 rounded-lg bg-green-50 text-green-600 hover:bg-green-100 transition-colors"
														title="Approve"
													>
														<UserCheck class="w-4 h-4" />
													</button>
												{/if}
												
												{#if userItem.user_id !== currentUser?.user_id}
													<button
														on:click={() => deleteUser(userItem.user_id)}
														class="p-2 rounded-lg bg-gray-50 text-gray-600 hover:bg-red-50 hover:text-red-600 transition-colors"
														title="Delete"
													>
														<Trash2 class="w-4 h-4" />
													</button>
												{/if}
											</div>
										</td>
									</tr>
								{/each}
							{/if}
						</tbody>
					</table>
				</div>
			</div>

			<!-- Results count -->
			<div class="mt-4 text-sm text-gray-600 text-center">
				Showing {filteredUsers.length} of {allUsers.length} users
			</div>
		</div>
	</main>
</div>
