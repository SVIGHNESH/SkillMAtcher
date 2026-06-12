<script lang="ts">
	import FileDropZone from '$lib/components/FileDropZone.svelte';
	import ResultsCard from '$lib/components/ResultsCard.svelte';
	import { matchSkills, getReportUrl, type MatchResult } from '$lib/api';

	let jdFile = $state<File | null>(null);
	let resumeFile = $state<File | null>(null);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let result = $state<MatchResult | null>(null);
	let progressStep = $state(0);

	const canSubmit = $derived(jdFile !== null && resumeFile !== null && !loading);

	const progressMessages = [
		'INITIALIZING SCANNER...',
		'LOADING PERSONALITY MATRIX...',
		'EXTRACTING SKILL VECTORS...',
		'COMPARING DATA SETS...',
		'GENERATING OVERSEER REPORT...'
	];

	async function handleMatch() {
		if (!jdFile || !resumeFile) return;
		loading = true;
		error = null;
		result = null;
		progressStep = 0;

		const interval = setInterval(() => {
			if (progressStep < progressMessages.length - 1) {
				progressStep++;
			}
		}, 800);

		try {
			result = await matchSkills(jdFile, resumeFile);
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'UNKNOWN SYSTEM ERROR';
		} finally {
			clearInterval(interval);
			progressStep = progressMessages.length;
			loading = false;
		}
	}

	function reset() {
		jdFile = null;
		resumeFile = null;
		result = null;
		error = null;
		progressStep = 0;
	}
</script>

<div class="terminal-container">
	<header class="terminal-header animate-in">
		<div class="text-dim">ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM</div>
		<div class="text-dim">COPYRIGHT 2075-2077 ROBCO INDUSTRIES</div>
		<br/>
		<h1>> SKILLMATCHER_</h1>
		<div>VAULT-TEC AUTOMATED RESEARCH TERMINAL</div>
		<div>STATUS: <span class="text-warning">OPERATIONAL</span></div>
		<div>=============================================</div>
	</header>

	{#if !result}
		<section class="upload-section animate-in" style="animation-delay: 0.1s;">
			<div class="prompt" style="margin-bottom: 1rem;">PLEASE INSERT DATA DISKS:</div>
			
			<div class="upload-grid">
				<FileDropZone
					label="JOB_DESCRIPTION.TXT"
					onFile={(f) => { jdFile = f; error = null; }}
				/>
				<FileDropZone
					label="PERSONNEL_RECORD.TXT"
					onFile={(f) => { resumeFile = f; error = null; }}
				/>
			</div>
			<div class="action-row">
				<button onclick={handleMatch} disabled={!canSubmit} class="btn-primary">
					[ EXECUTE MATCH ]
				</button>
			</div>
		</section>

		{#if loading}
			<section class="progress-section animate-in" style="margin-top: 2rem;">
				<div class="box-border">
					{#each progressMessages as msg, i}
						<div style="opacity: {i <= progressStep ? 1 : 0.2};">
							<span class="prompt"></span> {msg}
							{#if i === progressStep && i < progressMessages.length - 1}
								<span class="cursor-blink"></span>
							{/if}
							{#if i < progressStep}
								<span class="text-dim"> [OK]</span>
							{/if}
						</div>
					{/each}
				</div>
			</section>
		{/if}

		{#if error}
			<section class="error-section animate-in" style="margin-top: 2rem;">
				<div class="box-border" style="border-color: var(--phosphor-error);">
					<div class="text-error">
						<span class="prompt"></span> FATAL EXCEPTION: {error}
					</div>
					<br/>
					<button onclick={() => error = null} class="btn-secondary">
						[ ACKNOWLEDGE ]
					</button>
				</div>
			</section>
		{/if}
	{/if}

	{#if result}
		<section class="result-section animate-in" style="animation-delay: 0.1s;">
			<ResultsCard
				matched={result.matched}
				missing={result.missing}
				rate={result.match_rate}
				reportUrl={result.report_url ? getReportUrl(result.report_url.split('/').pop()!) : null}
				onNewMatch={reset}
			/>
		</section>
	{/if}
</div>

<style>
	.terminal-container {
		max-width: 900px;
		margin: 0 auto;
		padding: 2rem;
		position: relative;
		z-index: 10;
	}

	.terminal-header {
		margin-bottom: 2rem;
	}

	.upload-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
		margin-bottom: 2rem;
	}

	.action-row {
		display: flex;
		justify-content: flex-start;
	}

	@media (max-width: 768px) {
		.upload-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
