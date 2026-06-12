<script lang="ts">
	import type { CategoryBreakdown } from '$lib/api';

	let { categories }: { categories: Record<string, CategoryBreakdown> } = $props();

	const rows = $derived(
		Object.entries(categories)
			.map(([name, b]) => {
				const matched = b.matched?.length ?? 0;
				const missing = b.missing?.length ?? 0;
				const total = matched + missing;
				return { name, matched, missing, total, pct: total ? (matched / total) * 100 : 0 };
			})
			.filter((r) => r.total > 0)
			.sort((a, b) => b.total - a.total)
	);
</script>

{#if rows.length}
	<div class="cats">
		{#each rows as row}
			<div class="row">
				<div class="meta">
					<span class="name">{row.name}</span>
					<span class="frac">{row.matched}/{row.total}</span>
				</div>
				<div class="track" role="img" aria-label="{row.name}: {row.matched} of {row.total} matched">
					<div class="fill" style="width:{row.pct}%;"></div>
				</div>
			</div>
		{/each}
	</div>
{/if}

<style>
	.cats { display: flex; flex-direction: column; gap: 0.95rem; }
	.row { display: flex; flex-direction: column; gap: 0.4rem; }
	.meta { display: flex; justify-content: space-between; align-items: baseline; }
	.name { font-weight: 600; font-size: 0.9rem; }
	.frac { font-family: var(--font-mono); font-size: 0.74rem; color: var(--ink-mute); }
	.track {
		height: 9px;
		border-radius: 99px;
		background: var(--paper-2);
		overflow: hidden;
		border: 1px solid var(--line);
	}
	.fill {
		height: 100%;
		border-radius: 99px;
		background: linear-gradient(90deg, var(--accent), var(--good));
		transition: width 0.9s cubic-bezier(0.22, 1, 0.36, 1);
	}
</style>
