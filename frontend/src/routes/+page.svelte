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
		'reading documents...',
		'extracting skills via LLM...',
		'comparing skill sets...',
		'generating report...'
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
			error = e instanceof Error ? e.message : 'Unknown error';
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

	const fileIcon = $derived.by(() => {
		if (jdFile) {
			const ext = jdFile.name.split('.').pop()?.toLowerCase();
			return `[${ext}]`;
		}
		return '[/]';
	});
</script>

<div class="page-content">
	<section class="hero animate-in">
		<h1 class="hero-title">
			<span class="hero-prefix">//</span>
			skill<br class="mobile-break" />matcher
		</h1>
		<p class="hero-sub">ai-powered resume &bull; job description analyzer</p>
	</section>

	{#if !result}
		<section class="upload-section animate-in" style="animation-delay: 0.1s;">
			<div class="prompt" style="margin-bottom: 0.75rem;">upload files</div>
			<div class="upload-grid">
				<div class="upload-col">
					<div class="status-line" style="margin-bottom:0.5rem; color:var(--text-muted);">
						<span class="highlight">JD</span> job description
					</div>
					<FileDropZone
						label="Job Description"
						icon={jdFile ? fileIcon : '[JD]'}
						onFile={(f) => { jdFile = f; error = null; }}
					/>
				</div>
				<div class="upload-col">
					<div class="status-line" style="margin-bottom:0.5rem; color:var(--text-muted);">
						<span class="highlight">RS</span> resume / cv
					</div>
					<FileDropZone
						label="Resume"
						icon="[RS]"
						onFile={(f) => { resumeFile = f; error = null; }}
					/>
				</div>
			</div>
		</section>

		<section class="action-section animate-in" style="animation-delay: 0.2s;">
			<button
				onclick={handleMatch}
				disabled={!canSubmit}
				class="btn-primary execute-btn"
			>
				{loading ? 'processing' : 'execute match'}
				<span class="btn-arrow">{loading ? '...' : '>>'}</span>
			</button>
		</section>

		{#if loading}
			<section class="progress-section animate-in-fast">
				<div class="card" style="padding:1rem 1.5rem;">
					{#each progressMessages as msg, i}
						<div class="status-line" style="opacity: {i <= progressStep ? 1 : 0.25}; transition: opacity 0.4s;">
							<span class="highlight" style="color:{i <= progressStep ? 'var(--accent)' : 'var(--text-dim)'}">
								{i < progressStep ? '>>' : '>'}
							</span>
							{msg}
							{#if i === progressStep && i < progressMessages.length - 1}
								<span style="color:var(--accent); animation: cursorBlink 0.8s step-end infinite;">_</span>
							{/if}
							{#if i < progressStep}
								<span class="success-text" style="margin-left:0.5rem;">[ok]</span>
							{/if}
						</div>
					{/each}
					<div class="progress-bar" style="margin-top:1rem;"></div>
				</div>
			</section>
		{/if}

		{#if error}
			<section class="error-section animate-in-fast">
				<div class="card" style="border-color: var(--error-glow);">
					<div class="status-line">
						<span class="error-text">[!] error:</span> {error}
					</div>
					<button onclick={() => error = null} class="btn-secondary" style="margin-top:0.75rem;">
						dismiss
					</button>
				</div>
			</section>
		{/if}
	{/if}

	{#if result}
		<section class="result-section animate-in" style="animation-delay: 0.15s;">
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
	.page-content {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.hero {
		text-align: center;
		padding: 0.5rem 0 0.5rem;
	}

	.hero-title {
		font-family: var(--font-heading);
		font-size: 3.2rem;
		font-weight: 700;
		letter-spacing: 0.04em;
		line-height: 1.1;
		text-transform: lowercase;
		color: var(--text-primary);
	}

	.hero-prefix {
		color: var(--accent);
		opacity: 0.5;
		margin-right: 0.25rem;
		font-weight: 400;
	}

	.hero-sub {
		font-family: var(--font-mono);
		font-size: 0.78rem;
		color: var(--text-muted);
		margin-top: 0.6rem;
		letter-spacing: 0.05em;
	}

	.mobile-break {
		display: none;
	}

	.upload-section {
		width: 100%;
	}

	.upload-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.25rem;
	}

	.upload-col {
		display: flex;
		flex-direction: column;
	}

	.action-section {
		display: flex;
		justify-content: center;
	}

	.execute-btn {
		padding: 1rem 3rem;
		font-size: 1.05rem;
	}

	.btn-arrow {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		opacity: 0.7;
	}

	.progress-section {
		max-width: 600px;
		margin: 0 auto;
		width: 100%;
	}

	.error-section {
		max-width: 600px;
		margin: 0 auto;
		width: 100%;
	}

	.result-section {
		width: 100%;
	}

	@media (max-width: 700px) {
		.upload-grid {
			grid-template-columns: 1fr;
		}
		.hero-title {
			font-size: 2.2rem;
		}
		.mobile-break {
			display: inline;
		}
	}
</style>
