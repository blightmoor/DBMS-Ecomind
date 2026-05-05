<script>
  import { page } from '$app/stores';
  import { FileText, Grid3X3, LogOut, Sun, Moon, Zap, Home, Menu, X } from 'lucide-svelte';
  import { user, clearUser } from '../../../stores';
  import { goto } from '$app/navigation';

  const navItems = [
    { label: 'Home', href: '/home', icon: Home },
    { label: 'Carbon Tracking', href: '/carbon', icon: Zap },
    { label: 'Reports', href: '/reports', icon: FileText },
    { label: 'Settings', href: '/settings', icon: Grid3X3 }
  ];

  let showLogoutModal = false;
  let isSidebarOpen = false;

  async function confirmLogout() {
    clearUser();
    goto('/');
  }

  function toggleSidebar() {
    isSidebarOpen = !isSidebarOpen;
  }

  function closeSidebar() {
    isSidebarOpen = false;
  }

  // Export the toggle function so parent components can use it
  export { toggleSidebar };
</script>

<!-- Mobile Menu Button (visible only on small screens) -->
<button 
  on:click={toggleSidebar}
  class="mobile-menu-btn"
>
  {#if isSidebarOpen}
    <X />
  {:else}
    <Menu />
  {/if}
</button>

<!-- Mobile Backdrop -->
{#if isSidebarOpen}
  <div 
    class="mobile-backdrop"
    on:click={closeSidebar}
    role="button"
    tabindex="0"
    on:keydown={(e) => e.key === 'Enter' && closeSidebar()}
  ></div>
{/if}

<aside class="sidebar {isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}">
  <!-- Logo + Nav -->
  <div class="sidebar-content">
    <div class="logo-section">
      <div class="logo-icon">
        <Zap />
      </div>
      <span class="logo-text">Carbon Track</span>
    </div>

    <nav class="nav-section">
      {#each navItems as { label, href, icon: Icon }}
        <a
          href={href}
          class="nav-item {href === $page.url.pathname ? 'nav-item-active' : ''}"
          on:click={closeSidebar}
        >
          <Icon />
          <span>{label}</span>
        </a>
      {/each}
    </nav>
  </div>

  <!-- Theme Toggle + User -->
  <div class="sidebar-footer">
    <!-- Theme Toggle -->
    <div class="theme-toggle">
      <button class="theme-btn theme-btn-active">
        <Sun />
        Light
      </button>
      <button class="theme-btn">
        <Moon />
        Dark
      </button>
    </div>

    <!-- User Info -->
    {#if $user}
      <div class="user-info">
        <div class="user-header">
          <div class="user-avatar">
            {$user.name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div class="user-details">
            <p class="user-name">{$user.name || 'User'}</p>
            <p class="user-email">{$user.email || ''}</p>
          </div>
        </div>
      </div>
    {/if}
  </div>
</aside>

{#if showLogoutModal}
  <!-- Fullscreen Backdrop + Modal -->
  <div class="modal-backdrop">
    <div class="modal-content">
      <p class="modal-title">Are you sure you want to logout?</p>
      <div class="modal-actions">
        <button
          on:click={() => (showLogoutModal = false)}
          class="modal-btn modal-btn-cancel"
        >
          Cancel
        </button>
        <button
          on:click={confirmLogout}
          class="modal-btn modal-btn-logout"
        >
          Logout
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Mobile Menu Button */
  .mobile-menu-btn {
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 50;
    padding: 0.5rem;
    background-color: #16a34a;
    color: white;
    border-radius: 0.5rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    border: none;
    cursor: pointer;
    transition: background-color 0.15s;
    display: none;
  }

  .mobile-menu-btn:hover {
    background-color: #15803d;
  }

  .mobile-menu-btn :global(svg) {
    width: 1.5rem;
    height: 1.5rem;
  }

  /* Mobile Backdrop */
  .mobile-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 30;
    display: none;
  }

  /* Sidebar */
  .sidebar {
    width: 14rem;
    height: 100vh;
    background-color: white;
    border-right: 1px solid #e5e7eb;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 1.5rem 0;
    z-index: 40;
    position: fixed;
    top: 0;
    left: 0;
    transition: transform 0.3s ease-in-out;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  }

  .sidebar-closed {
    transform: translateX(-100%);
  }

  .sidebar-open {
    transform: translateX(0);
  }

  /* Sidebar Content */
  .sidebar-content {
    padding: 0 1.5rem;
  }

  .logo-section {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2.5rem;
  }

  .logo-icon {
    height: 3.5rem;
    width: 3.5rem;
    background-color: #16a34a;
    border-radius: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .logo-icon :global(svg) {
    width: 2rem;
    height: 2rem;
  }

  .logo-text {
    font-size: 1.5rem;
    font-weight: bold;
    color: #16a34a;
  }

  .nav-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    font-size: 1rem;
    font-weight: 500;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 0.5rem;
    transition: all 0.15s;
    text-decoration: none;
    color: #4b5563;
  }

  .nav-item:hover {
    color: #1f2937;
    background-color: #f9fafb;
  }

  .nav-item :global(svg) {
    width: 1.25rem;
    height: 1.25rem;
  }

  .nav-item-active {
    background-color: #f0fdf4;
    color: #15803d;
    font-weight: 600;
    border-left: 4px solid #16a34a;
  }

  /* Sidebar Footer */
  .sidebar-footer {
    padding: 0 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    font-size: 1.125rem;
  }

  .theme-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
  }

  .theme-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    border: none;
    cursor: pointer;
    background: none;
    color: #9ca3af;
  }

  .theme-btn :global(svg) {
    width: 1rem;
    height: 1rem;
  }

  .theme-btn-active {
    color: #374151;
    background-color: #f0fdf4;
  }

  /* User Info */
  .user-info {
    background-color: #f9fafb;
    border-radius: 0.5rem;
    padding: 1rem;
  }

  .user-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .user-avatar {
    width: 2.5rem;
    height: 2.5rem;
    background-color: #16a34a;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
  }

  .user-details {
    flex: 1;
    min-width: 0;
  }

  .user-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #111827;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0;
  }

  .user-email {
    font-size: 0.75rem;
    color: #6b7280;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0;
  }

  /* .user-meta {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.75rem;
  }

  .meta-row {
    display: flex;
    justify-content: space-between;
  }

  .meta-label {
    color: #6b7280;
  }

  .meta-value {
    color: #374151;
    text-transform: capitalize;
  }

  .logout-btn {
    width: 100%;
    margin-top: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    color: #dc2626;
    background: none;
    border: none;
    padding: 0.5rem 0.75rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }

  .logout-btn:hover {
    color: #b91c1c;
    background-color: #fef2f2;
  }

  .logout-btn :global(svg) {
    width: 1rem;
    height: 1rem;
  } */

  /* Modal */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 50;
  }

  .modal-content {
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    padding: 1.5rem;
    width: 100%;
    max-width: 24rem;
    text-align: center;
  }

  .modal-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 1rem 0;
  }

  .modal-actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
  }

  .modal-btn {
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    border: none;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.15s;
  }

  .modal-btn-cancel {
    background-color: #e5e7eb;
    color: #374151;
  }

  .modal-btn-cancel:hover {
    background-color: #d1d5db;
  }

  .modal-btn-logout {
    background-color: #ef4444;
    color: white;
  }

  .modal-btn-logout:hover {
    background-color: #dc2626;
  }

  /* Responsive Design */
  @media (max-width: 1023px) {
    .mobile-menu-btn {
      display: block;
    }

    .mobile-backdrop {
      display: block;
    }
  }

  @media (min-width: 1024px) {
    .sidebar {
      position: static;
      transform: translateX(0) !important;
      box-shadow: none;
    }
  }
</style>