<script>
  import { Zap, Home, FileText, Grid3X3, LogOut } from 'lucide-svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { clearUser } from '../../../stores';
  
  // Page title mapping based on route
  const pageIcons = {
    '/': { icon: Home, title: 'AI Powered Carbon FootPrint' },
    '/home': { icon: Home, title: 'Dashboard' },
    '/carbon': { icon: Zap, title: 'Carbon Tracking' },
    '/reports': { icon: FileText, title: 'Reports' },
    '/settings': { icon: Grid3X3, title: 'Settings' }
  };

  // Get current page info
  $: currentPageInfo = pageIcons[$page.url.pathname] || { icon: Home, title: 'AI Powered Carbon FootPrint' };
  $: Icon = currentPageInfo.icon;
  $: title = currentPageInfo.title;

  let showLogoutModal = false;

  function handleLogout() {
    clearUser();
    goto('/');
  }
</script>

<header class="h-16 w-full bg-white border-b border-gray-200 flex items-center justify-between px-4 sm:px-6 lg:px-8">
  <!-- Dynamic Title with Icon -->
  <div class="flex items-center gap-3 text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 ml-12 lg:ml-0">
    <svelte:component this={Icon} class="w-5 h-5 sm:w-6 sm:h-6 text-green-600" />
    <span class="truncate">{title}</span>
  </div>

  <!-- Logout Button -->
  <button
    on:click={() => (showLogoutModal = true)}
    class="flex items-center gap-2 px-3 py-2 sm:px-4 sm:py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors font-medium text-sm sm:text-base"
  >
    <LogOut class="w-4 h-4" />
    <span class="hidden sm:block">Logout</span>
  </button>
</header>

{#if showLogoutModal}
  <!-- Fullscreen Backdrop + Modal -->
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-sm text-center">
      <p class="text-lg font-semibold text-gray-800 mb-4">Are you sure you want to logout?</p>
      <div class="flex justify-center gap-4">
        <button
          on:click={() => (showLogoutModal = false)}
          class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
        >
          Cancel
        </button>
        <button
          on:click={handleLogout}
          class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    </div>
  </div>
{/if}