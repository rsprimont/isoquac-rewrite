<script lang="ts">
  import { page } from '$app/stores';

  // Svelte 5 Rune for reactivity
  let isOpen = $state(true);

  // Simple menu items data
  const menuItems = [
    { name: 'Home', href: '/' },
    { name: 'Job', href: '/analysis' },
    { name: 'Design of Experiments', href: '/doe' },
    { name: 'Visualisation', href: '/settings' },
    { name: 'Tools', href: '/tools' },
    { name: 'Tutorials', href: '/tutorials' },
    { name: 'Documentation', href: '/documentation' },
    { name: 'References', href: '/references' },
    { name: 'About', href: '/about' }
  ];

  function toggleSidebar() {
    isOpen = !isOpen;
  }
</script>

<aside 
  class="h-screen bg-yellow-300 text-white flex flex-col transition-all duration-200 shadow-xl/30
  {isOpen ? 'w-64' : 'w-20'}"
>
  
  <div class="p-4 flex flex-col gap-4">
    <div class="font-bold text-xl text-slate-900 flex items-center gap-2 h-11 overflow-hidden whitespace-nowrap">
    <a href="/" class="inline-block">
      <img src="/isoquac.png" alt="IsoQuac Logo" class="h-11 w-11 flex-shrink-0 inline-block" />

      <span class="{isOpen ? 'opacity-100' : 'opacity-0'} ml-2 text-xl no-underline hover:drop-shadow-xl/10 transition-opacity duration-200">
        IsoQuaC
      </span>
        </a>
    </div>

    <button 
      onclick={toggleSidebar} 
      class="p-2 hover:bg-yellow-400 rounded-md text-slate-900 transition-colors w-fit"
      aria-label="Toggle Menu"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
  </div>

  <nav class="flex-1 px-2 pt-2 space-y-2">
    {#each menuItems as item}
      <a 
        href={item.href}
        class="{isOpen ? 'opacity-100 block' : 'opacity-0 hidden'} flex items-center gap-4 px-3 py-3 rounded-lg transition-colors whitespace-nowrap
        {$page.url.pathname === item.href ? 'bg-yellow-100 text-slate-900 font-bold' : 'hover:bg-yellow-200 text-slate-900'}"
      >
        <span class="{isOpen ? 'opacity-100 block' : 'opacity-0 hidden'} transition-opacity duration-200">
          {item.name}
        </span>
      </a>
    {/each}
  </nav>

</aside>