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

	function rateColor(r: number): string {
		if (r >= 70) return 'var(--success)';
		if (r >= 40) return 'var(--warning)';
		return 'var(--error)';
	}
</script>

<div class="page-content">
	<section class="hero-mini animate-in">
		<div class="prompt">match history / log</div>
		<div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.75rem;">
			<h1>session records</h1>
			<a href="/" class="btn-primary" style="padding:0.45rem 1.1rem; font-size:0.78rem;">
				&#x21B1; new match
			</a>
		</div>
	</section>

	<section class="animate-in" style="animation-delay:0.08s;">
		{#if loading}
			<div class="card status-line" style="text-align:center; color:var(--text-muted);">
				<span class="highlight">loading</span> fetching records...
			</div>
		{:else if error}
			<div class="card" style="border-color:var(--error-glow); text-align:center;">
				<div class="status-line">
					<span class="error-text">[!] {error}</span>
				</div>
				<div class="status-line" style="margin-top:0.5rem; font-size:0.72rem; color:var(--text-muted);">
					is the backend running on port 8000?
				</div>
			</div>
		{:else if items.length === 0}
			<div class="card status-line" style="text-align:center;">
				no records found.
				<a href="/" class="highlight" style="margin-left:0.3rem;">run your first match</a>
			</div>
		{:else}
			<div class="log-list">
				{#each items as item, i}
					<div class="log-entry animate-in-fast" style="animation-delay: {i * 0.04}s;">
						<div class="log-meta">
							<span class="log-rate" style="color:{rateColor(item.match_rate)};">
								{item.match_rate.toFixed(0)}%
							</span>
							<span class="log-id">#{item.id}</span>
						</div>
						<div class="log-body">
							<div class="log-files">
								<span class="log-file highlight">{item.jd_filename}</span>
								<span class="log-vs">vs</span>
								<span class="log-file">{item.resume_filename}</span>
							</div>
							<div class="log-stats status-line" style="font-size:0.7rem;">
								{item.matched_skills.length} matched &bull;
								{item.missing_skills.length} missing &bull;
								{item.created_at}
							</div>
						</div>
						<div class="log-actions">
							<a href={getReportUrl(item.report_filename)} download class="btn-secondary" style="padding:0.3rem 0.75rem; font-size:0.7rem;">
								&#x2193; report
							</a>
							<button onclick={() => handleDelete(item.id)} class="btn-secondary btn-danger" style="padding:0.3rem 0.75rem; font-size:0.7rem;">
								&#x2715;
							</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</section>
</div>

<style>
	.page-content {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.hero-mini {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.hero-mini h1 {
		font-family: var(--font-heading);
		font-size: 1.5rem;
		font-weight: 600;
		text-transform: lowercase;
		letter-spacing: 0.03em;
	}

	.log-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.log-entry {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 0.9rem 1.25rem;
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		transition: all 0.2s;
	}

	.log-entry:hover {
		border-color: var(--border-active);
		background: var(--bg-card-hover);
	}

	.log-meta {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.15rem;
		min-width: 52px;
	}

	.log-rate {
		font-family: var(--font-heading);
		font-size: 1.15rem;
		font-weight: 700;
		line-height: 1;
	}

	.log-id {
		font-family: var(--font-mono);
		font-size: 0.6rem;
		color: var(--text-dim);
	}

	.log-body {
		flex: 1;
		min-width: 0;
	}

	.log-files {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-family: var(--font-mono);
		font-size: 0.82rem;
		flex-wrap: wrap;
	}

	.log-file {
		color: var(--text-primary);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 180px;
	}

	.log-vs {
		color: var(--text-dim);
		font-size: 0.7rem;
	}

	.log-stats {
		margin-top: 0.2rem;
	}

	.log-actions {
		display: flex;
		gap: 0.4rem;
		shrink: 0;
	}

	@media (max-width: 640px) {
		.log-entry {
			flex-direction: column;
			align-items: flex-start;
			gap: 0.6rem;
		}
		.log-meta {
			flex-direction: row;
			gap: 0.5rem;
		}
		.log-actions {
			align-self: flex-end;
		}
	}
</style>
