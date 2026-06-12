<script lang="ts">
	import MatchGauge from './MatchGauge.svelte';

	let {
		matched = [],
		missing = [],
		rate = 0,
		reportUrl = null,
		onNewMatch,
	}: {
		matched?: string[];
		missing?: string[];
		rate?: number;
		reportUrl?: string | null;
		onNewMatch?: () => void;
	} = $props();

	const total = $derived(matched.length + missing.length);
</script>

<div class="card results-card animate-in">
	<div class="prompt">match complete &mdash; {total} skills analyzed</div>

	<div class="results-grid">
		<div class="gauge-section">
			<MatchGauge {rate} />
		</div>

		<div class="lists-section">
			<div class="list-column">
				<div class="section-header">
					<h3 style="color: var(--success);">Matched</h3>
					<span class="badge-count" style="background: var(--success-dim); color: var(--success);">
						{matched.length}
					</span>
					<div class="line"></div>
				</div>
				<div class="skills-list">
					{#if matched.length === 0}
						<span class="empty-hint">none matched</span>
					{:else}
						{#each matched as skill, i}
							<span class="skill-badge matched" style="animation-delay: {i * 0.04}s;">
								{skill}
							</span>
						{/each}
					{/if}
				</div>
			</div>

			<div class="list-column">
				<div class="section-header">
					<h3 style="color: var(--error);">Missing</h3>
					<span class="badge-count" style="background: var(--error-glow); color: var(--error);">
						{missing.length}
					</span>
					<div class="line"></div>
				</div>
				<div class="skills-list">
					{#if missing.length === 0}
						<span class="empty-hint">none &mdash; perfect match</span>
					{:else}
						{#each missing as skill, i}
							<span class="skill-badge missing" style="animation-delay: {i * 0.04}s;">
								{skill}
							</span>
						{/each}
					{/if}
				</div>
			</div>
		</div>
	</div>

	<div class="results-footer">
		{#if reportUrl}
			<a href={reportUrl} download class="btn-secondary">
				&#x2193; download report
			</a>
		{/if}
		<button onclick={onNewMatch} class="btn-primary" style="padding:0.5rem 1.25rem; font-size:0.8rem;">
			&#x21B1; new match
		</button>
	</div>
</div>

<style>
	.results-card {
		margin-top: 1rem;
	}

	.results-grid {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1.5rem;
		margin-bottom: 1.25rem;
	}

	.gauge-section {
		width: 100%;
		display: flex;
		justify-content: center;
	}

	.lists-section {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.5rem;
		width: 100%;
	}

	@media (max-width: 640px) {
		.lists-section {
			grid-template-columns: 1fr;
		}
	}

	.list-column {
		display: flex;
		flex-direction: column;
	}

	.skills-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.badge-count {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 24px;
		height: 24px;
		border-radius: 6px;
		font-family: var(--font-mono);
		font-size: 0.72rem;
		font-weight: 600;
		padding: 0 6px;
	}

	.empty-hint {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--text-dim);
		font-style: italic;
	}

	.results-footer {
		display: flex;
		gap: 0.75rem;
		justify-content: flex-end;
		padding-top: 1rem;
		border-top: 1px solid var(--border);
	}
</style>
