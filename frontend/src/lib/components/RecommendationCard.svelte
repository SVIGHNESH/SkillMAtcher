<script lang="ts">
	import type { GapAnalysis } from '$lib/api';

	let { analysis }: { analysis: GapAnalysis } = $props();

	const verdictTone = $derived(
		/strong/i.test(analysis.verdict)
			? 'good'
			: /moderate|partial/i.test(analysis.verdict)
				? 'mid'
				: 'bad'
	);
</script>

<div class="wrap">
	{#if analysis.summary || analysis.verdict}
		<div class="verdict">
			<span class="badge {verdictTone}">{analysis.verdict || 'Analysis'}</span>
			<p class="summary">{analysis.summary}</p>
		</div>
	{/if}

	{#if analysis.recommendations?.length}
		<div class="recs">
			<h4 class="recs-title">How to close the gap</h4>
			{#each analysis.recommendations as rec, i}
				<div class="rec rise" style="animation-delay:{Math.min(i * 0.06, 0.4)}s;">
					<div class="rec-skill">{rec.skill}</div>
					{#if rec.why_it_matters}
						<p class="rec-why">{rec.why_it_matters}</p>
					{/if}
					{#if rec.how_to_learn}
						<p class="rec-how"><span class="lead">Learn →</span> {rec.how_to_learn}</p>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.wrap { display: flex; flex-direction: column; gap: 1.5rem; }
	.verdict { display: flex; flex-direction: column; gap: 0.7rem; }
	.badge {
		align-self: flex-start;
		font-family: var(--font-mono);
		font-size: 0.72rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		padding: 0.35rem 0.75rem;
		border-radius: 99px;
		font-weight: 500;
	}
	.badge.good { background: var(--good-soft); color: var(--good); }
	.badge.mid { background: var(--mid-soft); color: var(--mid); }
	.badge.bad { background: var(--bad-soft); color: var(--bad); }
	.summary { color: var(--ink-soft); font-size: 1rem; line-height: 1.6; }

	.recs { display: flex; flex-direction: column; gap: 0.75rem; }
	.recs-title { font-size: 0.95rem; font-weight: 700; }
	.rec {
		padding: 1rem 1.1rem;
		border: 1px solid var(--line);
		border-left: 3px solid var(--accent);
		border-radius: var(--radius-sm);
		background: var(--card-hover);
	}
	.rec-skill { font-weight: 700; font-size: 0.98rem; margin-bottom: 0.3rem; }
	.rec-why { color: var(--ink-soft); font-size: 0.9rem; margin-bottom: 0.45rem; }
	.rec-how { color: var(--ink-soft); font-size: 0.9rem; }
	.lead { color: var(--accent); font-weight: 600; font-family: var(--font-mono); font-size: 0.78rem; }
</style>
