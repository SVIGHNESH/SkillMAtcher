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

<div class="box-border results-card animate-in">
	<div class="prompt" style="margin-bottom: 1rem;">SCAN COMPLETE - {total} VECTORS ANALYZED</div>

	<div class="results-grid">
		<MatchGauge {rate} />

		<div class="lists-section">
			<div class="list-column">
				<div class="list-header text-dim">
					--- MATCHED SKILLS [{matched.length}] ---
				</div>
				<ul class="ascii-list">
					{#if matched.length === 0}
						<li class="text-dim">NO MATCHES FOUND</li>
					{:else}
						{#each matched as skill}
							<li>[+] {skill.toUpperCase()}</li>
						{/each}
					{/if}
				</ul>
			</div>

			<div class="list-column">
				<div class="list-header text-dim">
					--- MISSING SKILLS [{missing.length}] ---
				</div>
				<ul class="ascii-list error-list">
					{#if missing.length === 0}
						<li class="text-dim">ALL PARAMETERS NOMINAL</li>
					{:else}
						{#each missing as skill}
							<li class="text-error">[-] {skill.toUpperCase()}</li>
						{/each}
					{/if}
				</ul>
			</div>
		</div>
	</div>

	<div class="results-footer">
		<br/>
		<div class="text-dim">=============================================</div>
		<br/>
		<div class="action-buttons">
			{#if reportUrl}
				<a href={reportUrl} download class="btn-secondary">
					[ DOWNLOAD REPORT ]
				</a>
			{/if}
			<button onclick={onNewMatch} class="btn-primary">
				[ RESET SCANNER ]
			</button>
		</div>
	</div>
</div>

<style>
	.results-card {
		margin-top: 1rem;
	}

	.results-grid {
		display: flex;
		flex-direction: column;
		gap: 2rem;
		margin-bottom: 2rem;
	}

	.lists-section {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
		width: 100%;
	}

	@media (max-width: 768px) {
		.lists-section {
			grid-template-columns: 1fr;
		}
	}

	.list-column {
		display: flex;
		flex-direction: column;
	}

	.list-header {
		margin-bottom: 1rem;
	}

	.ascii-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.ascii-list li {
		position: relative;
	}

	.error-list li {
		color: var(--phosphor-error);
	}

	.results-footer {
		margin-top: 2rem;
	}

	.action-buttons {
		display: flex;
		gap: 1rem;
		align-items: center;
	}
</style>
