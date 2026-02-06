<script lang="ts">
	import { page } from '$app/state';

	// Svelte 5 Rune for reactivity
	let isOpen = $state(true);

	// Simple menu items data
	const menuItems = [
		{ name: 'Home', href: '/' },
		{ name: 'Job', href: '/analysis' },
		{ name: 'Design of Experiments', href: '/doe' },
		{ name: 'Visualisation', href: '/visualisation' },
		{ name: 'Tools', href: '/tools' },
		{ name: 'Tutorials', href: '/documentation/tutorial' },
		{ name: 'Documentation', href: '/documentation' },
		{ name: 'References', href: '/references' },
		{ name: 'About', href: '/about' }
	];

	function toggleSidebar() {
		isOpen = !isOpen;
	}
</script>

<aside
	class="flex h-screen flex-col bg-yellow-300 text-white shadow-xl/30 transition-all duration-200
  {isOpen ? 'w-64' : 'w-20'}"
>
	<div class="flex flex-col gap-4 p-4">
		<div
			class="flex h-11 items-center gap-2 overflow-hidden text-xl font-bold whitespace-nowrap text-slate-900"
		>
			<a href="/" class="flex w-full flex-row items-center">
				<img src="/isoquac.png" alt="IsoQuac Logo" class="inline-block h-11 w-11 flex-shrink-0" />

				<span
					class="{isOpen
						? 'block'
						: 'hidden'} ml-2 text-xl no-underline transition-opacity duration-200 hover:drop-shadow-xl/10"
				>
					IsoQuaC
				</span>
			</a>
		</div>

		<button
			onclick={toggleSidebar}
			class="w-fit rounded-md p-2 text-slate-900 transition-colors hover:bg-yellow-400"
			aria-label="Toggle Menu"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class="h-6 w-6"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M4 6h16M4 12h16M4 18h16"
				/>
			</svg>
		</button>
	</div>

	<nav class="flex-1 space-y-2 px-2 pt-2">
		{#each menuItems as item}
			<a
				href={item.href}
				class="{isOpen
					? 'block opacity-100'
					: 'hidden opacity-0'} flex items-center gap-4 rounded-lg px-3 py-3 whitespace-nowrap transition-colors
        {page.url.pathname === item.href
					? 'bg-yellow-100 font-bold text-slate-900'
					: 'text-slate-900 hover:bg-yellow-200'}"
			>
				<span
					class="{isOpen
						? 'block opacity-100'
						: 'hidden opacity-0'} transition-opacity duration-200"
				>
					{item.name}
				</span>
			</a>
		{/each}
	</nav>
</aside>
