<script lang="ts">
	let { rate = 0 }: { rate?: number } = $props();

	const totalBlocks = 20;
	const filledBlocks = $derived(Math.round((rate / 100) * totalBlocks));
	const emptyBlocks = $derived(totalBlocks - filledBlocks);

	const bar = $derived('[' + '#'.repeat(filledBlocks) + '.'.repeat(emptyBlocks) + ']');
	
	const colorClass = $derived(rate >= 70 ? 'text-primary' : rate >= 40 ? 'text-warning' : 'text-error');
</script>

<div class="gauge-wrapper">
	<div class="gauge-title">MATCH RATE CALCULATION:</div>
	<div class="gauge-bar {colorClass}">
		{bar} {rate.toFixed(0)}%
	</div>
</div>

<style>
	.gauge-wrapper {
		margin: 1rem 0;
		font-family: var(--font-terminal);
	}
	.gauge-title {
		color: var(--phosphor-dim);
		margin-bottom: 0.5rem;
	}
	.gauge-bar {
		font-size: 32px;
		letter-spacing: 2px;
	}
	
	.text-primary {
		color: var(--phosphor-primary);
	}
	.text-warning {
		color: var(--phosphor-warning);
		text-shadow: 0 0 8px var(--phosphor-warning);
	}
	.text-error {
		color: var(--phosphor-error);
		text-shadow: 0 0 8px var(--phosphor-error);
	}
</style>
