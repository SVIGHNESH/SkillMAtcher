<script lang="ts">
	import type { MatchResult } from '$lib/api';
	import ResultsCard from './ResultsCard.svelte';

	let { items, jobDescription }: { items: MatchResult[]; jobDescription: string } = $props();

	let selected = $state(0);

	function tone(r: number) {
		return r >= 70 ? 'good' : r >= 40 ? 'mid' : 'bad';
	}
</script>

<div class="board">
	<header class="board-head card rise">
		<div>
			<span class="eyebrow">Ranked candidates</span>
			<h2 class="title">{items.length} resumes vs {jobDescription}</h2>
		</div>
	</header>

	<div class="rows">
		{#each items as item, i}
			<button
				class="row rise"
				class:active={selected === i}
				style="animation-delay:{Math.min(i * 0.05, 0.4)}s;"
				onclick={() => (selected = i)}
			>
				<span class="rank">#{i + 1}</span>
				<span class="rate {tone(item.match_rate)}">{item.match_rate.toFixed(0)}%</span>
				<span class="name">{item.resume}</span>
				<span class="counts">
					<span class="good">{item.matched.length}✓</span>
					<span class="bad">{item.missing.length}✕</span>
				</span>
			</button>
		{/each}
	</div>

	{#if items[selected]}
		{#key selected}
			<div class="detail rise">
				<ResultsCard result={items[selected]} showReset={false} />
			</div>
		{/key}
	{/if}
</div>

<style>
	.board { display: flex; flex-direction: column; gap: 1.25rem; }
	.board-head { padding: 1.25rem 1.5rem; }
	.title { font-size: 1.3rem; margin-top: 0.2rem; }

	.rows { display: flex; flex-direction: column; gap: 0.5rem; }
	.row {
		display: grid;
		grid-template-columns: auto auto 1fr auto;
		align-items: center;
		gap: 1rem;
		padding: 0.85rem 1.25rem;
		background: var(--card);
		border: 1px solid var(--line);
		border-radius: var(--radius-sm);
		cursor: pointer;
		text-align: left;
		font-family: var(--font-body);
		transition: border-color 0.2s, background 0.2s, transform 0.12s;
	}
	.row:hover { border-color: var(--line-strong); background: var(--card-hover); }
	.row.active { border-color: var(--accent); background: var(--accent-soft); }
	.row:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--accent-ring); }

	.rank { font-family: var(--font-mono); font-size: 0.8rem; color: var(--ink-mute); width: 2ch; }
	.rate {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 1.25rem;
		font-variant-numeric: tabular-nums;
		width: 3.5ch;
	}
	.rate.good { color: var(--good); }
	.rate.mid { color: var(--mid); }
	.rate.bad { color: var(--bad); }
	.name { font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.counts { display: flex; gap: 0.6rem; font-family: var(--font-mono); font-size: 0.8rem; }
	.counts .good { color: var(--good); }
	.counts .bad { color: var(--bad); }

	@media (max-width: 560px) {
		.row { grid-template-columns: auto auto 1fr; }
		.counts { display: none; }
	}
</style>
