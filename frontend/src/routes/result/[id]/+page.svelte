<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { getHistoryItem, type HistoryItem, type MatchResult, type GapAnalysis } from '$lib/api';
	import ResultsCard from '$lib/components/ResultsCard.svelte';

	let result = $state<MatchResult | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	function toResult(item: HistoryItem): MatchResult {
		const analysis = (item.recommendations ?? {}) as GapAnalysis;
		return {
			status: 'success',
			match_id: item.id,
			job_description: item.jd_filename,
			resume: item.resume_filename,
			matched: item.matched_skills,
			missing: item.missing_skills,
			total_jd_skills: item.total_jd,
			total_resume_skills: item.total_resume,
			match_rate: item.match_rate,
			report_url: `/api/report/${item.report_filename}`,
			categories: item.categories ?? {},
			analysis: {
				verdict: analysis.verdict ?? '',
				summary: analysis.summary ?? '',
				recommendations: analysis.recommendations ?? []
			}
		};
	}

	onMount(async () => {
		const id = Number($page.params.id);
		try {
			result = toResult(await getHistoryItem(id));
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'Not found';
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head><title>Match #{$page.params.id} · Signal</title></svelte:head>

<a href="/history" class="btn btn-ghost btn-sm back no-print">← All matches</a>

{#if loading}
	<div class="card pad center muted">Loading…</div>
{:else if error}
	<div class="card pad center err">
		<strong>{error}</strong>
		<p><a href="/history">Back to history</a></p>
	</div>
{:else if result}
	<ResultsCard {result} showReset={false} />
{/if}

<style>
	.back { margin-bottom: 1.25rem; }
	.pad { padding: 1.6rem; }
	.center { text-align: center; }
	.muted { color: var(--ink-mute); }
	.err strong { color: var(--bad); }
	.err p { margin-top: 0.4rem; }
</style>
