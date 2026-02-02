<script lang="ts">
	import './layout.css';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="flex h-screen flex-row overflow-hidden">
	<Sidebar />

	<div class="relative flex h-screen flex-1 flex-col overflow-y-auto">
		<main class="flex-1 p-8">{@render children()}</main>
		<Footer />
	</div>
</div>
