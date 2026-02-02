<script lang="ts">
	import { slide, fade } from 'svelte/transition';

	// State
	let data: any[] = [];
	let conditions: any[] = [];
	let step = 1;
	let errors: string[] = [];

	// Temporary inputs
	let msrunInput = '';
	let condInput = '';

	// --- Actions ---

	function addMsRun() {
		errors = [];
		if (!msrunInput || msrunInput.trim() === '') return;
		
		if (data.some((msrun) => msrun.name === msrunInput)) {
			errors = [...errors, 'MSRun already exists'];
			return;
		}

		data = [
			...data,
			{
				name: msrunInput,
				// UI state for Step 3 accordion
				ui_open: false, 
				conditions: conditions.map((condition) => {
					return {
						name: condition.name,
						selected: false,
						alias_channels: { values: [], alias_input: '', channel_input: '' }
					};
				})
			}
		];
		msrunInput = '';
	}

	function removeMsRun(index: number) {
		data.splice(index, 1);
		data = data; // Trigger reactivity
	}

	function addCondition() {
		errors = [];
		if (!condInput || condInput.trim() === '') return;
		
		if (conditions.some((cond) => cond.name === condInput)) {
			errors = [...errors, 'Condition already exists'];
			return;
		}

		const newCondition = { name: condInput, selected: false };
		conditions = [...conditions, newCondition];

		// Add this condition to all existing MSRuns
		data.forEach((element) => {
			element.conditions.push({
				name: condInput,
				selected: false,
				alias_channels: { values: [], alias_input: '', channel_input: '' }
			});
		});
		data = data; // Trigger reactivity
		condInput = '';
	}

	function removeCondition(index: number) {
		data.forEach((element) => {
			element.conditions.splice(index, 1);
		});
		conditions.splice(index, 1);
		conditions = conditions;
		data = data;
	}

	function addAliasChannel(msrun_index: number, condition_index: number) {
		const target = data[msrun_index].conditions[condition_index].alias_channels;
		const alias = target.alias_input;
		const channel = target.channel_input;

		if (!channel || channel.trim() === '') return;

		target.values.push({ channel: channel, alias: alias });
		target.alias_input = '';
		target.channel_input = '';
		data = data;
	}

	function removeAliasChannel(msrun_index: number, condition_index: number, alias_index: number) {
		data[msrun_index].conditions[condition_index].alias_channels.values.splice(alias_index, 1);
		data = data;
	}

	// --- Bulk Actions ---

	function checkAll() {
		data.forEach((element) => {
			element.conditions.forEach((condition: any) => {
				condition.selected = true;
			});
		});
		data = data;
	}

	function uncheckAll() {
		data.forEach((element) => {
			element.conditions.forEach((condition: any) => {
				condition.selected = false;
			});
		});
		data = data;
	}

	// --- Step Validation ---

	function stepOneCheck() {
		errors = [];
		if (data.length > 0 && conditions.length > 1) {
			step += 1;
		} else {
			errors = [...errors, 'Please add at least one MSRun and two conditions.'];
		}
	}

	function stepTwoCheck() {
		errors = [];
		let atleastOneSelected = data.every((msrun) =>
			msrun.conditions.some((condition: any) => condition.selected)
		);
		if (atleastOneSelected) {
			step += 1;
		} else {
			errors = [...errors, 'Please select at least one condition for each MSRun.'];
		}
	}

	function stepThreeCheck() {
		errors = [];
		// Check 1: Selected conditions must have at least one channel
		let atleastOneChannel = data.some((msrun) =>
			msrun.conditions.some((condition: any) =>
				condition.selected ? condition.alias_channels.values.length === 0 : false
			)
		);

		// Check 2: Consistency in aliases
		let aliasCheck = data.some((msrun) =>
			msrun.conditions.some((condition: any) => {
				if (!condition.selected) return false;

				let hasAtleastOneAlias = condition.alias_channels.values.some(
					(ac: any) => ac.alias.trim() !== ''
				);
				if (!hasAtleastOneAlias) return false;

				return condition.alias_channels.values.some((ac: any) => ac.alias.trim() === '');
			})
		);

		if (aliasCheck) {
			errors = [
				...errors,
				'If one channel has an alias in a condition, all channels should have an alias in that condition.'
			];
			return;
		}

		if (atleastOneChannel) {
			errors = [...errors, 'Please add at least one channel for each selected condition.'];
			return;
		}

		step += 1;
	}

	function backButton() {
		errors = [];
		step -= 1;
	}

	function download() {
		let fileContent = '';
		data.forEach((msrun) => {
			fileContent += `${msrun.name}\t`;
			msrun.conditions.forEach((condition: any) => {
				if (condition.selected) {
					fileContent += `${condition.name}:`;
					let alias_string = '';
					let channel_string = '';
					condition.alias_channels.values.forEach((alias: any) => {
						if (alias.alias.trim() !== '') {
							alias_string += `${alias.alias},`;
						}
						channel_string += `${alias.channel},`;
					});
					fileContent += `${channel_string.slice(0, -1)}`;
					if (alias_string.length > 0) {
						fileContent += `:${alias_string.slice(0, -1)}`;
					}
					fileContent += `\t`;
				}
			});
			fileContent = fileContent.slice(0, -1) + '\n';
		});

		let blob = new Blob([fileContent], { type: 'text/tsv' });
		let url = URL.createObjectURL(blob);
		let a = document.createElement('a'); // Created element dynamically instead of getting by ID
		a.href = url;
		a.download = 'doe.tsv';
		a.click();
        URL.revokeObjectURL(url);
	}
</script>

<div class="mx-auto rounded p-8 shadow-md md:w-5/6 lg:w-4/6 xl:w-3/6">
	<h1 class="page-title text-2xl font-bold mb-4">Create a new DoE file</h1>

	{#if step === 1}
		<div in:fade={{ duration: 200 }}>
			<div class="mb-4">
				<h3 class="text-lg font-bold">Step 1</h3>
				<p>Add at least one MSRun and two conditions. Each entry should be unique.</p>
			</div>
			
            {#each errors as error}
				<div>
					<p class="error mb-2 font-bold text-red-500">{error}</p>
				</div>
			{/each}

			<div class="flex min-w-full flex-row justify-between gap-8">
				<div class="w-1/2 grow-0">
					<label class="font-bold" for="msruninput">MSRuns</label>
					<div class="mb-4 flex min-w-full flex-row justify-between gap-4">
						<input
							class="border border-slate-500/50 rounded p-2 w-9/12 border p-2 rounded"
							id="msruninput"
							type="text"
							bind:value={msrunInput}
							on:keyup={(e) => e.key === 'Enter' && addMsRun()}
						/>
						<button class="w-3/12 text-center bg-yellow-300 font-bold shadow-lg rounded p-2" on:click={addMsRun}>Add</button>
					</div>
					<div class="flex flex-col gap-2">
						{#each data as msr, index}
							<div class="border border-slate-300 flex flex-row justify-between gap-2">
								<span
									class="my-auto inline-block w-10/12 grow-0 overflow-hidden text-ellipsis px-1"
								>
									{msr.name}
								</span>
								<button
									class="bg-red-500 hover:bg-red-700 text-white font-bold rounded-r hover:shadow-lg w-2/12 grow-0 rounded border border-l-2 py-2 text-center"
									on:click={() => removeMsRun(index)}
                                    aria-label="Delete MSRun {msr.name}"
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										stroke-width="1.5"
										stroke="currentColor"
										class="mx-auto h-6 w-6"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
										/>
									</svg>
								</button>
							</div>
						{/each}
					</div>
				</div>

				<div class="w-1/2 grow-0">
					<label class="font-bold" for="condinput">Conditions</label>
					<div class="mb-4 flex min-w-full flex-row justify-between gap-4">
						<input
							class="border border-slate-500/50 rounded p-2 w-9/12 border p-2 rounded"
							id="condinput"
							type="text"
							bind:value={condInput}
							on:keyup={(e) => e.key === 'Enter' && addCondition()}
						/>
						<button class="w-3/12 text-center bg-yellow-300 font-bold shadow-lg rounded p-2" on:click={addCondition}
							>Add</button
						>
					</div>
					<div class="flex flex-col gap-2">
						{#each conditions as cond, index}
							<div class="border border-slate-300 flex flex-row justify-between gap-2">
								<span
									class="my-auto inline-block w-10/12 grow-0 overflow-hidden text-ellipsis px-1"
								>
									{cond.name}
								</span>
								<button
									class="bg-red-500 hover:bg-red-700 text-white font-bold rounded-r hover:shadow-lg w-2/12 grow-0 rounded border border-l-2 py-2 text-center"
									on:click={() => removeCondition(index)}
                                    aria-label="Delete Condition {cond.name}"
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										stroke-width="1.5"
										stroke="currentColor"
										class="mx-auto h-6 w-6"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
										/>
									</svg>
								</button>
							</div>
						{/each}
					</div>
				</div>
			</div>
			<div class="mt-10 flex flex-row justify-between text-right">
				<div class="w-10/12"></div>
				<button class="w-2/12 text-center bg-yellow-300 font-bold shadow-lg rounded p-2" on:click={stepOneCheck}>Continue</button>
			</div>
		</div>
	{/if}

	{#if step === 2}
		<div class="min-w-fit max-w-full" in:fade={{ duration: 200 }}>
			<div class="mx-auto text-left">
				<h4 class="text-left text-lg font-bold">Step 2</h4>
				<h4 class="mb-4 text-left text-lg">
					For each MS run, indicate which conditions are represented by at least one quantification
					channel.
				</h4>
				<div class="mx-auto mb-4 flex flex-row justify-center gap-4">
					<button class="bg-yellow-300 hover:bg-yellow-500 text-slate-900 font-bold py-2 px-4 rounded shadow-md hover:shadow-lg" on:click={checkAll}>Check all</button>
					<button class="bg-yellow-300 hover:bg-yellow-500 text-slate-900 font-bold py-2 px-4 rounded shadow-md hover:shadow-lg" on:click={uncheckAll}>Uncheck all</button>
				</div>
                {#each errors as error}
                    <div>
                        <p class="error mb-2 font-bold text-red-500">{error}</p>
                    </div>
                {/each}
				<div class="grid grid-cols-3 gap-4 pb-8">
					{#each data as msr}
						<div>
							<p class="mb-1 text-lg font-bold">{msr.name}</p>
							<ul class="list-none">
								{#each msr.conditions as cond}
									<li class="mb-1">
										<input
											class="h-5 w-5 rounded border-gray-300 text-yellow-500 focus:ring-yellow-100"
											type="checkbox"
											bind:checked={cond.selected}
										/>
										<span>{cond.name}</span>
									</li>
								{/each}
							</ul>
						</div>
					{/each}
				</div>
				<div class="inset-x-0 bottom-0 text-right">
					<button class="pr-2 hover:underline" on:click={backButton}>Back</button>
					<button class="w-2/12 text-center bg-yellow-300 font-bold shadow-lg rounded p-2" on:click={stepTwoCheck}>Continue</button>
				</div>
			</div>
		</div>
	{/if}

	{#if step === 3}
		<div class="min-w-fit max-w-full" in:fade={{ duration: 200 }}>
			<div class="mx-auto text-left">
				<h4 class="text-left text-lg font-bold">Step 3</h4>
				<h4 class="mb-4 text-left text-lg">
					For each condition, list the names of the quantification channels as they appear in your
					data file.
				</h4>
				<h4 class="mb-4 text-lg">
					If you would like each channel to have a different name in the output files, please specify
					them in the Aliases field. If you define an alias for one channel in a certain condition,
					you must specify aliases for all channels in that condition.
				</h4>
			</div>
			
            {#each errors as error}
                <div>
                    <p class="error mb-2 font-bold text-red-500">{error}</p>
                </div>
            {/each}

			<div class="flex min-w-full flex-col justify-between">
				{#each data as msr, msr_index}
					<div class="mb-8 min-w-full rounded px-2 py-2 shadow-md">
						<div class="flex min-w-full flex-row justify-between gap-4">
							<h5 class="font-2xl min-h-full w-9/12 grow-0 align-middle">
								MSRun: <span class="font-bold">{msr.name}</span>
							</h5>
							<button
                                class="font-bold w-3/12 grow-0 rounded px-4 py-2 {msr.ui_open ? 'bg-gray-400 text-white' : 'bg-yellow-300'}"
								on:click={() => (msr.ui_open = !msr.ui_open)}
							>
								{msr.ui_open ? 'Close' : 'Open'}
							</button>
						</div>

						{#if msr.ui_open}
							<div transition:slide>
								{#each msr.conditions as cond, cond_index}
									{#if cond.selected}
										<div class="flex min-w-full flex-col justify-between gap-2 pb-8 pt-4 border-b border-b-slate-400 last:border-0">
											<div>
												<h6 class="font-lg">
													Condition: <span class="font-bold">{cond.name}</span>
												</h6>
											</div>
											<div class="min-w-full">
												<div class="flex w-full flex-col gap-2">
													<div class="mb-2 flex w-full flex-row gap-4">
														<input
															class="border border-slate-500/50 rounded p-2 w-5/12 grow-0 p-2 border rounded"
															type="text"
															bind:value={cond.alias_channels.channel_input}
															placeholder="Channel"
															on:keyup={(e) =>
																e.key === 'Enter' &&
																addAliasChannel(msr_index, cond_index)}
														/>
														<input
															class="border border-slate-500/50 rounded p-2 w-5/12 grow-0 p-2 border rounded"
															type="text"
															bind:value={cond.alias_channels.alias_input}
															placeholder="Alias"
															on:keyup={(e) =>
																e.key === 'Enter' &&
																addAliasChannel(msr_index, cond_index)}
														/>
														<button
															class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 rounded shadow-md hover:shadow-lg w-2/12 grow-0 rounded"
															on:click={() => addAliasChannel(msr_index, cond_index)}
                                                            aria-label="Add alias channel for Condition {cond.name} in MSRun {msr.name}"
														>
															<svg
																xmlns="http://www.w3.org/2000/svg"
																fill="none"
																viewBox="0 0 24 24"
																stroke-width="1.5"
																stroke="currentColor"
																class="mx-auto h-6 w-6"
															>
																<path
																	stroke-linecap="round"
																	stroke-linejoin="round"
																	d="M12 4.5v15m7.5-7.5h-15"
																/>
															</svg>
														</button>
													</div>
													{#each cond.alias_channels.values as alias, alias_index}
														<div class="flex w-full flex-row gap-4">
															<div class="w-5/12 grow-0 rounded border p-2">
																{alias.channel}
															</div>
															<div class="w-5/12 grow-0 rounded border p-2">
																{alias.alias}
															</div>
															<button
																class="bg-red-500 hover:bg-red-700 text-white font-bold rounded-r hover:shadow-lg w-2/12 grow-0 rounded py-2 text-right shadow-lg flex justify-center"
																on:click={() =>
																	removeAliasChannel(
																		msr_index,
																		cond_index,
																		alias_index
																	)}
                                                                aria-label="Delete alias channel {alias.channel} for Condition {cond.name} in MSRun {msr.name}"
															>
																<svg
																	xmlns="http://www.w3.org/2000/svg"
																	fill="none"
																	viewBox="0 0 24 24"
																	stroke-width="1.5"
																	stroke="currentColor"
																	class="mx-auto w-6 h-6 w-full"
																>
																	<path
																		stroke-linecap="round"
																		stroke-linejoin="round"
																		d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
																	/>
																</svg>
															</button>
														</div>
													{/each}
												</div>
											</div>
										</div>
									{/if}
								{/each}
							</div>
						{/if}
					</div>
				{/each}
			</div>

			<div class="inset-x-0 bottom-0 text-right">
				<button class="pr-2 hover:underline" on:click={backButton}>Back</button>
				<button class="bg-yellow-300 font-bold shadow-lg rounded px-4 py-2" on:click={stepThreeCheck}>Continue</button>
			</div>
		</div>
	{/if}

	{#if step === 4}
		<div in:fade={{ duration: 200 }}>
			<h4 class="text-left text-lg font-bold">Step 4</h4>
			<h4 class="mb-4 text-left text-lg">Ready to download file!</h4>
			
            {#each errors as error}
                <div>
                    <p class="error mb-2 font-bold text-red-500">{error}</p>
                </div>
            {/each}
            
			<div class="inset-x-0 bottom-0 text-right">
				<button class="hover:underline mr-4" on:click={backButton}>Back</button>
				<button class="bg-green-600 text-white px-4 py-2 rounded" on:click={download}>Download</button>
			</div>
		</div>
	{/if}
</div>