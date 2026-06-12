<script lang="ts">
	import InputSource from '$lib/components/InputSource.svelte';
	import FileDropZone from '$lib/components/FileDropZone.svelte';
	import ResultsCard from '$lib/components/ResultsCard.svelte';
	import ResumeLeaderboard from '$lib/components/ResumeLeaderboard.svelte';
	import {
		matchSkills,
		matchBatch,
		type MatchResult,
		type BatchMatchResult,
		type Source
	} from '$lib/api';

	let mode = $state<'single' | 'batch'>('single');

	// JD input
	let jdFile = $state<File | null>(null);
	let jdText = $state('');
	let jdMethod = $state<'upload' | 'paste'>('upload');

	// Single resume input
	let resumeFile = $state<File | null>(null);
	let resumeText = $state('');
	let resumeMethod = $state<'upload' | 'paste'>('upload');

	// Batch resumes
	let batchFiles = $state<File[]>([]);

	let loading = $state(false);
	let error = $state<string | null>(null);
	let result = $state<MatchResult | null>(null);
	let batchResult = $state<BatchMatchResult | null>(null);
	let progressStep = $state(0);

	const progressMessages = [
		'Reading documents',
		'Extracting skills with AI',
		'Comparing against the role',
		'Analysing the skill gap'
	];

	const jdReady = $derived(jdMethod === 'upload' ? !!jdFile : jdText.trim().length > 0);
	const resumeReady = $derived(
		resumeMethod === 'upload' ? !!resumeFile : resumeText.trim().length > 0
	);
	const canSubmit = $derived(
		!loading && jdReady && (mode === 'single' ? resumeReady : batchFiles.length > 0)
	);

	function jdSource(): Source {
		return jdMethod === 'paste' ? { text: jdText } : { file: jdFile! };
	}
	function resumeSource(): Source {
		return resumeMethod === 'paste' ? { text: resumeText } : { file: resumeFile! };
	}

	function addBatchFiles(e: Event) {
		const files = (e.target as HTMLInputElement).files;
		if (files) batchFiles = [...batchFiles, ...Array.from(files)];
	}
	function removeBatch(i: number) {
		batchFiles = batchFiles.filter((_, idx) => idx !== i);
	}

	async function run() {
		if (!canSubmit) return;
		loading = true;
		error = null;
		result = null;
		batchResult = null;
		progressStep = 0;

		const interval = setInterval(() => {
			if (progressStep < progressMessages.length - 1) progressStep++;
		}, 900);

		try {
			if (mode === 'single') {
				result = await matchSkills(jdSource(), resumeSource());
			} else {
				batchResult = await matchBatch(jdSource(), batchFiles);
			}
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'Something went wrong';
		} finally {
			clearInterval(interval);
			loading = false;
		}
	}

	function reset() {
		result = null;
		batchResult = null;
		error = null;
		progressStep = 0;
	}

	const hasResult = $derived(!!result || !!batchResult);
</script>

<svelte:head>
	<title>Signal — Skill Match Intelligence</title>
</svelte:head>

{#if !hasResult}
	<section class="hero rise">
		<span class="eyebrow">Resume ⟷ Job description</span>
		<h1>
			See exactly where a candidate<br />
			<span class="accent">fits — and where they don't.</span>
		</h1>
		<p class="lede">
			Signal reads a job description and a résumé, then uses AI to surface matched skills,
			gaps, and a concrete plan to close them.
		</p>
	</section>

	<div class="mode-row rise" style="animation-delay:0.06s;">
		<div class="mode-toggle" role="tablist" aria-label="Match mode">
			<button
				role="tab"
				aria-selected={mode === 'single'}
				class="mode"
				class:active={mode === 'single'}
				onclick={() => (mode = 'single')}>One résumé</button
			>
			<button
				role="tab"
				aria-selected={mode === 'batch'}
				class="mode"
				class:active={mode === 'batch'}
				onclick={() => (mode = 'batch')}>Rank several</button
			>
		</div>
	</div>

	<section class="card panel rise" style="animation-delay:0.1s;">
		<div class="inputs">
			<InputSource
				label="Job description"
				placeholder="Paste the job description…"
				bind:file={jdFile}
				bind:text={jdText}
				bind:method={jdMethod}
			/>

			{#if mode === 'single'}
				<InputSource
					label="Résumé"
					placeholder="Paste the résumé…"
					bind:file={resumeFile}
					bind:text={resumeText}
					bind:method={resumeMethod}
				/>
			{:else}
				<div class="batch">
					<span class="batch-label">Résumés <span class="muted">({batchFiles.length})</span></span>
					<label class="batch-drop">
						<input type="file" accept=".txt,.pdf,.docx" multiple onchange={addBatchFiles} class="sr" />
						<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4M8 8l4-4 4 4" /><path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" /></svg>
						<span>Add résumés to rank</span>
					</label>
					{#if batchFiles.length}
						<ul class="batch-list">
							{#each batchFiles as f, i}
								<li>
									<span class="bf-name">{f.name}</span>
									<button class="bf-x" aria-label="Remove {f.name}" onclick={() => removeBatch(i)}>✕</button>
								</li>
							{/each}
						</ul>
					{/if}
				</div>
			{/if}
		</div>

		<div class="submit-row">
			<button class="btn btn-primary" onclick={run} disabled={!canSubmit}>
				{#if loading}Analysing…{:else}Analyse match{/if}
			</button>
			<span class="hint">Powered by Groq · llama-3.3-70b</span>
		</div>
	</section>

	{#if loading}
		<section class="card pad progress rise" style="margin-top:1.25rem;">
			{#each progressMessages as msg, i}
				<div class="pstep" class:done={i < progressStep} class:active={i === progressStep}>
					<span class="pdot">
						{#if i < progressStep}✓{:else if i === progressStep}<span class="spin"></span>{/if}
					</span>
					<span>{msg}</span>
				</div>
			{/each}
		</section>
	{/if}

	{#if error}
		<section class="card pad err rise" style="margin-top:1.25rem;">
			<strong>Couldn't complete the match.</strong>
			<p>{error}</p>
			<button class="btn btn-ghost btn-sm" onclick={() => (error = null)}>Dismiss</button>
		</section>
	{/if}
{:else}
	<div class="result-wrap">
		<button class="btn btn-ghost btn-sm back no-print" onclick={reset}>← New match</button>
		{#if result}
			<ResultsCard {result} onNewMatch={reset} />
		{:else if batchResult}
			<ResumeLeaderboard items={batchResult.items} jobDescription={batchResult.job_description} />
		{/if}
	</div>
{/if}

<style>
	.hero { text-align: center; max-width: 46rem; margin: 1rem auto 2.25rem; }
	.hero h1 {
		font-size: clamp(2.1rem, 5.5vw, 3.4rem);
		margin: 0.8rem 0 1rem;
	}
	.hero .accent { color: var(--accent); }
	.lede { color: var(--ink-soft); font-size: 1.1rem; line-height: 1.6; max-width: 38rem; margin: 0 auto; }

	.mode-row { display: flex; justify-content: center; margin-bottom: 1.1rem; }
	.mode-toggle {
		display: inline-flex;
		gap: 0.2rem;
		padding: 0.25rem;
		background: var(--paper-2);
		border: 1px solid var(--line);
		border-radius: 99px;
	}
	.mode {
		font-family: var(--font-body);
		font-weight: 600;
		font-size: 0.88rem;
		padding: 0.45rem 1.1rem;
		border: none;
		background: transparent;
		color: var(--ink-mute);
		border-radius: 99px;
		cursor: pointer;
		transition: color 0.2s, background 0.2s;
	}
	.mode:hover { color: var(--ink); }
	.mode.active { background: var(--card); color: var(--accent); box-shadow: var(--shadow-sm); }

	.panel { padding: 1.75rem; }
	.inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }

	.submit-row {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-top: 1.6rem;
		flex-wrap: wrap;
	}
	.submit-row .hint { font-family: var(--font-mono); font-size: 0.72rem; color: var(--ink-mute); }

	/* Batch */
	.batch { display: flex; flex-direction: column; gap: 0.7rem; }
	.batch-label { font-weight: 700; font-size: 0.95rem; }
	.batch-label .muted { color: var(--ink-mute); font-weight: 400; }
	.sr { position: absolute; width: 1px; height: 1px; opacity: 0; }
	.batch-drop {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 1.5rem;
		min-height: 120px;
		border: 1.5px dashed var(--line-strong);
		border-radius: var(--radius);
		background: var(--card);
		color: var(--ink-mute);
		cursor: pointer;
		font-weight: 500;
		transition: border-color 0.2s, background 0.2s;
	}
	.batch-drop:hover { border-color: var(--accent); background: var(--accent-soft); }
	.batch-list { list-style: none; display: flex; flex-direction: column; gap: 0.35rem; }
	.batch-list li {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
		padding: 0.5rem 0.8rem;
		background: var(--card-hover);
		border: 1px solid var(--line);
		border-radius: var(--radius-sm);
		font-size: 0.85rem;
	}
	.bf-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.bf-x { border: none; background: none; color: var(--ink-mute); cursor: pointer; font-size: 0.8rem; }
	.bf-x:hover { color: var(--bad); }

	/* Progress */
	.progress { display: flex; flex-direction: column; gap: 0.9rem; }
	.pstep { display: flex; align-items: center; gap: 0.8rem; color: var(--ink-mute); transition: color 0.3s; }
	.pstep.active, .pstep.done { color: var(--ink); }
	.pdot {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 22px;
		height: 22px;
		border-radius: 99px;
		border: 1.5px solid var(--line-strong);
		font-size: 0.7rem;
		color: var(--good);
		flex-shrink: 0;
	}
	.pstep.done .pdot { border-color: var(--good); background: var(--good-soft); }
	.pstep.active .pdot { border-color: var(--accent); }
	.spin {
		width: 9px;
		height: 9px;
		border: 2px solid var(--accent-ring);
		border-top-color: var(--accent);
		border-radius: 99px;
		animation: spin 0.7s linear infinite;
	}
	@keyframes spin { to { transform: rotate(360deg); } }

	.err { border-color: color-mix(in srgb, var(--bad) 35%, var(--line)); display: flex; flex-direction: column; gap: 0.5rem; align-items: flex-start; }
	.err strong { color: var(--bad); }
	.err p { color: var(--ink-soft); font-size: 0.92rem; }

	.pad { padding: 1.6rem; }
	.result-wrap { display: flex; flex-direction: column; gap: 1rem; }
	.back { align-self: flex-start; }

	@media (max-width: 720px) {
		.inputs { grid-template-columns: 1fr; }
	}
</style>
