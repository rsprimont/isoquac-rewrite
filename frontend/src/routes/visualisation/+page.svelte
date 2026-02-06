<script lang="ts">
	import Chart from 'chart.js/auto';
	import JSZip from 'jszip';
	import { fade } from 'svelte/transition';

	// --- Types ---
	type VolcanoPoint = { x: number; y: number; label: string; originalIndex: number };
	type JitterRow = {
		protein: string;
		sequence: string;
		channel: string;
		modifications: string;
		condition: string;
		intensity: number;
		isReferenceCondition: number;
	};
	type ProteinMetric = {
		name: string;
		sampleSize: number;
		metric: number | null;
	};

	// --- State: UI ---
	let activeTab = $state('volcano'); // 'volcano' | 'jitter'
	let fileUploaded = $state(false);
	let errorMsg = $state('');
	let conditions: string[] = $state([]);
	let selectedCondition = $state('');

	// --- State: Data ---
	let volcanoRawData: any[] = $state([]);
	let volcanoData: VolcanoPoint[] = $state([]);
	let volcanoSelectedIndices: number[] = $state([]); // Indices into volcanoData

	let jitterRawData: JitterRow[] = $state([]);
	let jitterSortedProteins: ProteinMetric[] = $state([]);
	let jitterSortKey: 'name' | 'sampleSize' | 'metric' = $state('name');
	let jitterSortOrder: 'asc' | 'desc' = $state('asc');

	// --- Charts ---
	let volcanoCanvas: HTMLCanvasElement;
	let jitterCanvas: HTMLCanvasElement;
	let volcanoChart: Chart | undefined;
	let jitterChart: Chart | undefined;

	// --- Helpers ---
	const tsvJSON = (tsv: string) => {
		const lines = tsv.trim().split('\n');
		const headers = lines[0].split('\t').map((h) => h.trim());
		const result = [];
		for (let i = 1; i < lines.length; i++) {
			const obj: any = {};
			const currentline = lines[i].split('\t');
			if (currentline.length < headers.length) continue;
			for (let j = 0; j < headers.length; j++) {
				obj[headers[j]] = currentline[j]?.trim();
			}
			result.push(obj);
		}
		return result;
	};

	// --- File Handling ---
	async function handleFileUpload(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (!file) return;

		errorMsg = '';
		fileUploaded = false;

		if (file.type === 'application/zip' || file.name.endsWith('.zip')) {
			const zip = new JSZip();
			try {
				const zipContent = await zip.loadAsync(file);

				// 1. Process Volcano Data
				const tsvFileName = Object.keys(zipContent.files).find((name) =>
					name.endsWith('_results_minimal.tsv')
				);
				if (tsvFileName) {
					const tsvData = await zipContent.files[tsvFileName].async('string');
					setupVolcanoData(tsvData);
				} else {
					errorMsg = "Error: No '_results_minimal.tsv' file found.";
				}

				// 2. Process Jitter Data
				const jitterFileName = 'peptideData.tsv';
				if (zipContent.files[jitterFileName]) {
					const tsvData = await zipContent.files[jitterFileName].async('string');
					setupJitterData(tsvData);
				} else {
					// Not a hard error if jitter is missing, but good to note
					console.warn("No 'peptideData.tsv' file found.");
				}

				fileUploaded = true;
			} catch (err: any) {
				errorMsg = 'Error extracting zip: ' + err.message;
			}
		} else {
			errorMsg = 'Please upload a valid .zip file.';
		}
	}

	// --- Volcano Logic ---
	function setupVolcanoData(tsvData: string) {
		volcanoRawData = tsvJSON(tsvData);
		const headers = Object.keys(volcanoRawData[0]);

		// Extract conditions from headers like "adjusted p-value (ConditionA)"
		conditions = headers
			.filter((h) => h.includes('adjusted p-value') || h.includes('log2 fold change'))
			.map((h) => h.match(/\((.*?)\)/)?.[1])
			.filter((v, i, a) => v && a.indexOf(v) === i) as string[];

		if (conditions.length > 0) {
			selectedCondition = conditions[0];
			updateVolcanoPlot();
			selectSmallestPoints();
		}
	}

	function updateVolcanoPlot() {
		if (!selectedCondition) return;
		if (volcanoChart) volcanoChart.destroy();

		const log2fcKey = `log2 fold change (${selectedCondition})`;
		const pvalKey = `adjusted p-value (${selectedCondition})`;

		// 1. Update the State variable (for the Table UI)
		volcanoData = volcanoRawData
			.map((d, i) => ({
				x: parseFloat(d[log2fcKey]),
				y: parseFloat(d[pvalKey]),
				label: d['protein'],
				originalIndex: i
			}))
			.filter((d) => d.y > 0 && !isNaN(d.y));

		const minVal = Math.min(...volcanoData.map((d) => d.y)) * 1e-1;

		// 2. Create a "Clean" copy for Chart.js
		// We map it to new objects so Chart.js doesn't touch our Svelte State Proxies
		const chartData = volcanoData.map((d) => ({ ...d }));

		const config = {
			type: 'scatter' as const,
			data: {
				datasets: [
					{
						label: selectedCondition,
						data: chartData, // <--- USE THE CLEAN COPY HERE
						backgroundColor: 'rgba(75, 192, 192, 1)',
						pointRadius: 5,
						// Initialize plain array for colors
						pointBackgroundColor: new Array(chartData.length).fill('blue')
					}
				]
			},
			options: {
				// ... (rest of options remain exactly the same)
				responsive: true,
				animation: false,
				onClick: handleVolcanoClick,
				plugins: {
					tooltip: {
						callbacks: {
							label: (ctx: any) => ctx.raw.label
						}
					}
				},
				scales: {
					x: {
						type: 'linear' as const,
						title: { display: true, text: 'log2(fold change)' }
					},
					y: {
						type: 'logarithmic' as const,
						reverse: true,
						ticks: {
							callback: (val: any) => Number(val).toExponential(0)
						},
						title: { display: true, text: '-log10(p-value)' },
						suggestedMin: minVal,
						suggestedMax: 1.0
					}
				}
			}
		};

		// @ts-ignore
		volcanoChart = new Chart(volcanoCanvas, config);
	}

	function handleVolcanoClick(event: any, elements: any[]) {
		if (!volcanoChart || elements.length === 0) return;
		const index = elements[0].index;
		toggleVolcanoPoint(index);
	}

	function toggleVolcanoPoint(index: number) {
		const dataset = volcanoChart!.data.datasets[0];
		const colorArray = dataset.pointBackgroundColor as string[];

		if (volcanoSelectedIndices.includes(index)) {
			volcanoSelectedIndices = volcanoSelectedIndices.filter((i) => i !== index);
			colorArray[index] = 'blue';
		} else {
			volcanoSelectedIndices = [...volcanoSelectedIndices, index];
			colorArray[index] = 'red';
		}
		volcanoChart!.update();
	}

	function selectSmallestPoints() {
		if (!volcanoChart) return;

		// Sort by p-value (y), take top 5
		const top5Indices = volcanoData
			.map((val, idx) => ({ idx, y: val.y }))
			.sort((a, b) => a.y - b.y)
			.slice(0, 5)
			.map((item) => item.idx);

		// Clear current
		clearVolcanoSelection();

		// Add new
		top5Indices.forEach((idx) => toggleVolcanoPoint(idx));
	}

	function clearVolcanoSelection() {
		if (!volcanoChart) return;
		const dataset = volcanoChart.data.datasets[0];
		volcanoSelectedIndices.forEach((idx) => {
			(dataset.pointBackgroundColor as string[])[idx] = 'blue';
		});
		volcanoSelectedIndices = [];
		volcanoChart.update();
	}

	// --- Jitter Logic ---
	function setupJitterData(tsvData: string) {
		const raw = tsvJSON(tsvData);

		jitterRawData = raw
			.map((row: any) => ({
				protein: row['Master Protein Accessions'],
				sequence: row['Sequence'],
				channel: row['channel'],
				modifications: row['Modifications'],
				condition: row['condition'],
				intensity: parseFloat(row['intensity']),
				isReferenceCondition: row['isReferenceCondition'] === '1' ? 1 : 0
			}))
			.filter((row) => !isNaN(row.intensity));

		// Calculate Stats for Table
		const proteinStats: Record<
			string,
			{ refSum: number; refCount: number; nonRefSum: number; nonRefCount: number }
		> = {};
		const counts: Record<string, number> = {};

		jitterRawData.forEach((row) => {
			if (!proteinStats[row.protein]) {
				proteinStats[row.protein] = { refSum: 0, refCount: 0, nonRefSum: 0, nonRefCount: 0 };
				counts[row.protein] = 0;
			}
			counts[row.protein]++;
			if (row.isReferenceCondition) {
				proteinStats[row.protein].refSum += row.intensity;
				proteinStats[row.protein].refCount++;
			} else {
				proteinStats[row.protein].nonRefSum += row.intensity;
				proteinStats[row.protein].nonRefCount++;
			}
		});

		jitterSortedProteins = Object.entries(counts).map(([name, sampleSize]) => {
			const stat = proteinStats[name];
			let metric: number | null = null;
			if (stat.refCount > 0 && stat.nonRefCount > 0) {
				const diff = stat.refSum / stat.refCount - stat.nonRefSum / stat.nonRefCount;
				metric = Math.pow(diff, 2);
			}
			return { name, sampleSize, metric };
		});

		sortJitterTable('name'); // Default sort

		// Select first protein
		if (jitterSortedProteins.length > 0) {
			updateJitterPlot(jitterSortedProteins[0].name);
		}
	}

	function sortJitterTable(key: 'name' | 'sampleSize' | 'metric') {
		if (jitterSortKey === key) {
			jitterSortOrder = jitterSortOrder === 'asc' ? 'desc' : 'asc';
		} else {
			jitterSortKey = key;
			jitterSortOrder = 'asc';
		}

		jitterSortedProteins = jitterSortedProteins.sort((a, b) => {
			const valA = a[key];
			const valB = b[key];
			if (valA === null) return 1;
			if (valB === null) return -1;

			if (typeof valA === 'string' && typeof valB === 'string') {
				return jitterSortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
			}
			// Numeric sort
			return jitterSortOrder === 'asc'
				? (valA as number) - (valB as number)
				: (valB as number) - (valA as number);
		});
	}

	function updateJitterPlot(proteinName: string) {
		if (jitterChart) jitterChart.destroy();
		// Wait for DOM update if switching tabs, though canvas should exist
		if (!jitterCanvas) return;

		const proteinData = jitterRawData.filter((r) => r.protein === proteinName);
		const uniqueConditions = [...new Set(proteinData.map((r) => r.condition))];

		const dataset = proteinData.map((row) => ({
			x: addJitter(uniqueConditions.indexOf(row.condition)),
			y: row.intensity,
			label: row.modifications !== '[]' ? `${row.sequence} (${row.modifications})` : row.sequence,
			isRef: row.isReferenceCondition
		}));

		const config = {
			type: 'scatter' as const,
			data: {
				datasets: [
					{
						label: proteinName,
						data: dataset,
						backgroundColor: dataset.map((d) => (d.isRef ? 'red' : 'blue')),
						pointRadius: 5
					}
				]
			},
			options: {
				responsive: true,
				animation: false,
				plugins: {
					tooltip: {
						callbacks: {
							label: (ctx: any) => ctx.raw.label
						}
					}
				},
				scales: {
					x: {
						type: 'linear' as const,
						title: { display: true, text: 'Condition' },
						ticks: {
							callback: (val: any) => uniqueConditions[val] || ''
						},
						// Add padding so points don't hit edges
						min: -0.5,
						max: uniqueConditions.length - 0.5
					},
					y: {
						type: 'linear' as const,
						title: { display: true, text: 'Intensity' }
					}
				}
			}
		};

		// @ts-ignore
		jitterChart = new Chart(jitterCanvas, config);
	}

	function addJitter(value: number, range = 0.1) {
		return value + (Math.random() * range - range / 2);
	}

	// --- Reactivity ---
	// If the user switches tabs, we need to ensure the chart renders (canvas might have been hidden)
	// In Svelte 5, effects track dependencies automatically.
	$effect(() => {
		if (activeTab === 'jitter' && jitterSortedProteins.length > 0 && !jitterChart) {
			// Re-render the last selected or first one
			// We need a tiny tick for the canvas to be in DOM if using x-show logic (which we replaced with if blocks usually, but here we keep structure)
			setTimeout(() => updateJitterPlot(jitterSortedProteins[0].name), 0);
		}
	});
</script>

<div class="mx-auto rounded bg-white p-4 shadow-md md:w-5/6 lg:w-5/6 xl:w-4/6">
	<h1 class="pb-4 text-2xl font-semibold text-gray-900">Visualization</h1>

	<div class="mb-4 flex justify-center gap-2">
		<div class="flex w-3/5">
			<button
				class="cursor-pointer border border-gray-300 px-4 py-2 transition-colors"
				class:bg-gray-100={activeTab === 'volcano'}
				class:font-bold={activeTab === 'volcano'}
				class:text-gray-900={activeTab === 'volcano'}
				class:text-gray-500={activeTab !== 'volcano'}
				onclick={() => (activeTab = 'volcano')}
			>
				Volcano Plot
			</button>
			<button
				class="cursor-pointer border border-l-0 border-gray-300 px-4 py-2 transition-colors"
				class:bg-gray-100={activeTab === 'jitter'}
				class:font-bold={activeTab === 'jitter'}
				class:text-gray-900={activeTab === 'jitter'}
				class:text-gray-500={activeTab !== 'jitter'}
				onclick={() => (activeTab = 'jitter')}
			>
				Jitter Plot
			</button>
		</div>
		<div class="w-2/5 pt-1">
			<input
				type="file"
				accept=".zip"
				onchange={handleFileUpload}
				class="w-full cursor-pointer rounded text-sm font-medium text-slate-500 shadow-sm file:mr-4 file:cursor-pointer file:border-0 file:bg-yellow-300 file:px-4 file:py-2 file:text-slate-900 file:hover:bg-yellow-500"
			/>
			<p class="py-2 text-center text-sm text-slate-500">
				Download example file <a
					class="font-bold text-blue-600 underline"
					href="/example-data/results.zip">here</a
				>
			</p>
		</div>
	</div>

	{#if errorMsg}
		<p class="mb-4 text-center font-bold text-red-500">{errorMsg}</p>
	{/if}

	<div class={activeTab === 'volcano' ? 'block' : 'hidden'}>
		{#if fileUploaded}
			<div class="mb-4 flex justify-center">
				<label for="conditionDropdown" class="mr-2 font-bold">Select condition:</label>
				<select
					id="conditionDropdown"
					bind:value={selectedCondition}
					onchange={updateVolcanoPlot}
					class="rounded border border-gray-300 bg-white px-2 py-1"
				>
					{#each conditions as cond}
						<option value={cond}>{cond}</option>
					{/each}
				</select>
			</div>
		{/if}

		<div class="relative min-h-[20rem] w-full">
			<canvas bind:this={volcanoCanvas}></canvas>
		</div>

		{#if volcanoSelectedIndices.length > 0}
			<div class="mt-4 min-w-max" transition:fade>
				<h2 class="mb-2 text-lg font-bold">Selected points</h2>
				<table class="w-full table-auto rounded border">
					<thead class="bg-gray-100">
						<tr>
							<th class="p-2 text-left">Protein</th>
							<th class="p-2 text-left">p-value</th>
							<th class="p-2 text-left">log2(fc)</th>
							<th class="p-2 text-left">Link</th>
						</tr>
					</thead>
					<tbody>
						{#each volcanoSelectedIndices as idx}
							<tr class="border-b last:border-0">
								<td class="p-2">{volcanoData[idx].label}</td>
								<td class="p-2">{Number(volcanoData[idx].y).toExponential(4)}</td>
								<td class="p-2">{Number(volcanoData[idx].x).toExponential(4)}</td>
								<td class="p-2">
									<a
										class="text-blue-600 hover:underline"
										href={`https://www.uniprot.org/uniprot/${volcanoData[idx].label}`}
										target="_blank"
									>
										Link
									</a>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
				<div class="mt-2">
					<button
						class="rounded bg-yellow-300 px-4 py-2 font-bold text-slate-900 shadow-md hover:bg-yellow-500 hover:shadow-lg"
						onclick={clearVolcanoSelection}
					>
						Clear selection
					</button>
				</div>
			</div>
		{/if}
	</div>

	<div class={activeTab === 'jitter' ? 'block' : 'hidden'}>
		<div class="mb-4 flex flex-col">
			<div class="flex flex-col overflow-hidden rounded border border-gray-300">
				<div class="flex border-b border-gray-300 bg-gray-100 font-bold">
					<button
						class="w-1/3 p-2 text-left hover:bg-gray-200"
						onclick={() => sortJitterTable('name')}
					>
						Protein
					</button>
					<button
						class="w-1/3 p-2 text-left hover:bg-gray-200"
						onclick={() => sortJitterTable('sampleSize')}
					>
						Sample Size
					</button>
					<button
						class="w-1/3 p-2 text-left hover:bg-gray-200"
						onclick={() => sortJitterTable('metric')}
					>
						Sq Mean Diff
					</button>
					<div class="w-1/3 p-2"></div>
				</div>
				<div class="flex max-h-48 flex-col overflow-y-auto">
					{#each jitterSortedProteins as p (p.name)}
						<div class="flex items-center border-b border-gray-300 hover:bg-gray-50">
							<div class="w-1/3 truncate p-2" title={p.name}>{p.name}</div>
							<div class="w-1/3 p-2">{p.sampleSize}</div>
							<div class="w-1/3 p-2">{p.metric !== null ? p.metric.toFixed(2) : 'N/A'}</div>
							<div class="w-1/3 p-2 text-right">
								<button
									class="rounded bg-yellow-300 px-3 py-1 text-sm font-bold text-gray-900 hover:bg-yellow-500"
									onclick={() => updateJitterPlot(p.name)}
								>
									Select
								</button>
							</div>
						</div>
					{/each}
					{#if jitterSortedProteins.length === 0}
						<div class="p-4 text-center text-gray-500">No data loaded yet. Upload a zip file.</div>
					{/if}
				</div>
			</div>
		</div>

		<div class="relative min-h-[20rem] w-full">
			<canvas bind:this={jitterCanvas}></canvas>
		</div>
	</div>
</div>
