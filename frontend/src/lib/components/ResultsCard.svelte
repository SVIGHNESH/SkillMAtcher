<script lang="ts">
	import type { MatchResult } from '$lib/api';
	import { getReportUrl } from '$lib/api';
	import ScoreRing from './ScoreRing.svelte';
	import SkillChips from './SkillChips.svelte';
	import CategoryBreakdown from './CategoryBreakdown.svelte';
	import RecommendationCard from './RecommendationCard.svelte';

	let {
		result,
		onNewMatch,
		showReset = true
	}: { result: MatchResult; onNewMatch?: () => void; showReset?: boolean } = $props();

	const reportFile = $derived(result.report_url ? result.report_url.split('/').pop()! : null);
	const hasCats = $derived(Object.keys(result.categories ?? {}).length > 0);
</script>

<div class="results">
	<header class="summary card rise">
		<div class="ring-wrap">
			<ScoreRing rate={result.match_rate} />
		</div>
		<div class="summary-text">
			<span class="eyebrow">Match report</span>
			<h2 class="files">
				<span class="jd">{result.job_description}</span>
				<span class="vs">vs</span>
				<span class="rs">{result.resume}</span>
			</h2>
			<div class="stats">
				<div class="stat">
					<span class="num good">{result.matched.length}</span>
					<span class="lbl">Matched</span>
				</div>
				<div class="stat">
					<span class="num bad">{result.missing.length}</span>
					<span class="lbl">Missing</span>
				</div>
				<div class="stat">
					<span class="num">{result.total_jd_skills}</span>
					<span class="lbl">JD skills</span>
				</div>
			</div>
			<div class="actions no-print">
				{#if reportFile}
					<a class="btn btn-ghost btn-sm" href={getReportUrl(reportFile, 'txt')} download>↓ TXT</a>
					<a class="btn btn-ghost btn-sm" href={getReportUrl(reportFile, 'json')} target="_blank" rel="noopener">↓ JSON</a>
				{/if}
				<button class="btn btn-ghost btn-sm" onclick={() => window.print()}>⎙ PDF</button>
				{#if showReset && onNewMatch}
					<button class="btn btn-primary btn-sm" onclick={onNewMatch}>New match</button>
				{/if}
			</div>
		</div>
	</header>

	{#if result.analysis && (result.analysis.summary || result.analysis.recommendations?.length)}
		<section class="card pad rise" style="animation-delay:0.05s;">
			<RecommendationCard analysis={result.analysis} />
		</section>
	{/if}

	<div class="grid">
		<section class="card pad rise" style="animation-delay:0.1s;">
			<SkillChips title="Matched skills" skills={result.matched} variant="good" />
			<div class="divider"></div>
			<SkillChips title="Missing skills" skills={result.missing} variant="bad" />
		</section>

		{#if hasCats}
			<section class="card pad rise" style="animation-delay:0.15s;">
				<span class="eyebrow">By category</span>
				<h3 class="cat-title">Coverage breakdown</h3>
				<CategoryBreakdown categories={result.categories} />
			</section>
		{/if}
	</div>
</div>

<style>
	.results { display: flex; flex-direction: column; gap: 1.25rem; }

	.summary {
		display: flex;
		gap: 1.75rem;
		align-items: center;
		padding: 1.75rem;
	}
	.ring-wrap { flex-shrink: 0; }
	.summary-text { display: flex; flex-direction: column; gap: 0.6rem; min-width: 0; }
	.files {
		font-size: 1.5rem;
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.5rem;
	}
	.files .jd { color: var(--ink); }
	.files .vs { font-size: 0.85rem; color: var(--ink-mute); font-family: var(--font-mono); font-weight: 400; }
	.files .rs { color: var(--ink-soft); font-weight: 600; font-size: 1.15rem; font-family: var(--font-body); }

	.stats { display: flex; gap: 1.75rem; margin-top: 0.3rem; }
	.stat { display: flex; flex-direction: column; }
	.num {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 1.6rem;
		font-variant-numeric: tabular-nums;
		line-height: 1;
	}
	.num.good { color: var(--good); }
	.num.bad { color: var(--bad); }
	.lbl { font-family: var(--font-mono); font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--ink-mute); }

	.actions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.6rem; }

	.pad { padding: 1.6rem; }
	.divider { height: 1px; background: var(--line); margin: 1.4rem 0; }

	.grid {
		display: grid;
		grid-template-columns: 1.5fr 1fr;
		gap: 1.25rem;
		align-items: start;
	}
	.cat-title { font-size: 1.1rem; margin: 0.2rem 0 1.1rem; }

	@media (max-width: 820px) {
		.summary { flex-direction: column; text-align: center; align-items: center; }
		.stats { justify-content: center; }
		.actions { justify-content: center; }
		.grid { grid-template-columns: 1fr; }
	}

	@media print {
		.no-print { display: none !important; }
	}
</style>
