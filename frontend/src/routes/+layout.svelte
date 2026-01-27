<script lang="ts">
	import './layout.css';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
  </svelte:head>

<div class="flex flex-row min-h-screen bg-gray-100">
  <Sidebar />

  <main class="flex-1 p-8 overflow-y-auto h-screen">
    {@render children()} 
  </main>
</div>
