<script lang="ts">
	import { onMount } from 'svelte';
	import { getHistory, deleteHistoryItem, getReportUrl, type HistoryItem } from '$lib/api';

	let items = $state<HistoryItem[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			const res = await getHistory(50, 0);
			items = res.items;
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'Failed to load history';
		} finally {
			loading = false;
		}
	});

	async function handleDelete(id: number) {
		try {
			await deleteHistoryItem(id);
			items = items.filter((i) => i.id !== id);
		} catch (e: unknown) {
			alert(e instanceof Error ? e.message : 'Delete failed');
		}
	}

	function tone(r: number) {
		return r >= 70 ? 'good' : r >= 40 ? 'mid' : 'bad';
	}
	function when(s: string) {
		const d = new Date(s.includes('Z') || s.includes('T') ? s : s.replace(' ', 'T') + 'Z');
		return isNaN(d.getTime()) ? s : d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
	}
</script>

<svelte:head><title>History · Signal</title></svelte:head>

<section class="head rise">
	<div>
		<span class="eyebrow">Saved analyses</span>
		<h1>Match history</h1>
	</div>
	<a href="/" class="btn btn-primary btn-sm">New match</a>
</section>

{#if loading}
	<div class="card pad center muted rise">Loading saved matches…</div>
{:else if error}
	<div class="card pad center rise err">
		<strong>{error}</strong>
		<p>Is the API running on port 8000?</p>
	</div>
{:else if items.length === 0}
	<div class="card pad center muted rise">
		No matches yet. <a href="/">Run your first match →</a>
	</div>
{:else}
	<div class="grid">
		{#each items as item, i}
			<article class="card item rise" style="animation-delay:{Math.min(i * 0.04, 0.5)}s;">
				<div class="ring {tone(item.match_rate)}">
					<span>{item.match_rate.toFixed(0)}<small>%</small></span>
				</div>
				<div class="body">
					<a class="files" href="/result/{item.id}">
						<span class="jd">{item.jd_filename}</span>
						<span class="vs">vs {item.resume_filename}</span>
					</a>
					<div class="meta">
						<span class="good">{item.matched_skills.length} matched</span>
						<span class="bad">{item.missing_skills.length} missing</span>
						<span class="time">{when(item.created_at)}</span>
					</div>
				</div>
				<div class="acts">
					<a class="btn btn-ghost btn-sm" href="/result/{item.id}">View</a>
					<a class="btn btn-ghost btn-sm" href={getReportUrl(item.report_filename, 'txt')} download aria-label="Download report">↓</a>
					<button class="btn btn-ghost btn-sm danger" onclick={() => handleDelete(item.id)} aria-label="Delete">✕</button>
				</div>
			</article>
		{/each}
	</div>
{/if}

<style>
	.head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-bottom: 1.5rem; }
	.head h1 { font-size: 2rem; margin-top: 0.3rem; }

	.pad { padding: 1.6rem; }
	.center { text-align: center; }
	.muted { color: var(--ink-mute); }
	.err strong { color: var(--bad); display: block; }
	.err p { color: var(--ink-soft); margin-top: 0.3rem; }

	.grid { display: flex; flex-direction: column; gap: 0.75rem; }
	.item {
		display: flex;
		align-items: center;
		gap: 1.25rem;
		padding: 1rem 1.25rem;
		transition: border-color 0.2s, box-shadow 0.2s, transform 0.12s;
	}
	.item:hover { border-color: var(--line-strong); box-shadow: var(--shadow-md); transform: translateY(-1px); }

	.ring {
		flex-shrink: 0;
		width: 56px;
		height: 56px;
		display: grid;
		place-items: center;
		border-radius: 99px;
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 1.05rem;
		font-variant-numeric: tabular-nums;
		border: 2px solid currentColor;
	}
	.ring small { font-size: 0.65rem; }
	.ring.good { color: var(--good); background: var(--good-soft); }
	.ring.mid { color: var(--mid); background: var(--mid-soft); }
	.ring.bad { color: var(--bad); background: var(--bad-soft); }

	.body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.3rem; }
	.files { display: flex; flex-direction: column; color: var(--ink); }
	.files:hover .jd { color: var(--accent); }
	.jd { font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.vs { font-size: 0.82rem; color: var(--ink-mute); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.meta { display: flex; flex-wrap: wrap; gap: 0.9rem; font-family: var(--font-mono); font-size: 0.72rem; }
	.meta .good { color: var(--good); }
	.meta .bad { color: var(--bad); }
	.meta .time { color: var(--ink-mute); }

	.acts { display: flex; gap: 0.35rem; flex-shrink: 0; }
	.acts .danger:hover { color: var(--bad); border-color: var(--bad); }

	@media (max-width: 600px) {
		.item { flex-wrap: wrap; }
		.acts { width: 100%; justify-content: flex-end; }
	}
</style>
