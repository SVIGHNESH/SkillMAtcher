<script lang="ts">
	let { rate = 0 }: { rate?: number } = $props();

	const radius = 48;
	const stroke = 6;
	const circumference = $derived(2 * Math.PI * radius);
	const offset = $derived(circumference - (rate / 100) * circumference);
	const color = $derived(rate >= 70 ? '#00e676' : rate >= 40 ? '#ff9100' : '#ff1744');
	const glowColor = $derived(rate >= 70 ? 'rgba(0,230,118,0.15)' : rate >= 40 ? 'rgba(255,145,0,0.15)' : 'rgba(255,23,68,0.15)');

	let mounted = $state(false);
	$effect(() => { mounted = true; });
</script>

<div class="gauge-wrapper">
	<svg width="160" height="160" viewBox="0 0 160 160" class="gauge-svg">
		<defs>
			<filter id="glow-{rate.toFixed(0)}">
				<feGaussianBlur stdDeviation="3" result="blur" />
				<feMerge>
					<feMergeNode in="blur" />
					<feMergeNode in="SourceGraphic" />
				</feMerge>
			</filter>
		</defs>

		<circle cx="80" cy="80" r={radius}
			fill="none" stroke="#1a1e34" stroke-width={stroke} />
		<circle cx="80" cy="80" r={radius}
			fill="none" stroke={color} stroke-width={stroke}
			stroke-linecap="round"
			stroke-dasharray={circumference}
			stroke-dashoffset={mounted ? offset : circumference}
			transform="rotate(-90 80 80)"
			style="transition: stroke-dashoffset 1s cubic-bezier(0.34, 1.56, 0.64, 1), stroke 0.5s;"
			filter="url(#glow-{rate.toFixed(0)})" />

		{#if mounted}
			<circle cx="80" cy="80" r={radius - 2}
				fill="none" stroke={glowColor} stroke-width={stroke + 4}
				stroke-linecap="round"
				stroke-dasharray={circumference}
				stroke-dashoffset={offset}
				transform="rotate(-90 80 80)"
				style="transition: stroke-dashoffset 1s cubic-bezier(0.34, 1.56, 0.64, 1);" />
		{/if}

		<text x="80" y="68" text-anchor="middle" fill="#e8eaed"
			font-size="32" font-weight="700" font-family="'Chakra Petch', sans-serif">
			{rate.toFixed(0)}%
		</text>
		<text x="80" y="90" text-anchor="middle" fill="#4a4f70"
			font-size="9" font-family="'JetBrains Mono', monospace"
			letter-spacing="2">
			MATCH RATE
		</text>
	</svg>
</div>

<style>
	.gauge-wrapper {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.gauge-svg {
		display: block;
		filter: drop-shadow(0 0 20px rgba(0, 229, 255, 0.03));
	}
</style>
