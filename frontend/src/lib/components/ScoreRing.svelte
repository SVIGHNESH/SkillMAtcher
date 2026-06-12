<script lang="ts">
	let {
		rate = 0,
		size = 184,
		stroke = 14,
		label = 'Match'
	}: { rate?: number; size?: number; stroke?: number; label?: string } = $props();

	const r = $derived((size - stroke) / 2);
	const circ = $derived(2 * Math.PI * ((size - stroke) / 2));

	// Animated value sweeps from 0 → rate on mount.
	let shown = $state(0);
	$effect(() => {
		const target = rate;
		const reduce =
			typeof matchMedia !== 'undefined' &&
			matchMedia('(prefers-reduced-motion: reduce)').matches;
		if (reduce) {
			shown = target;
			return;
		}
		shown = 0;
		const start = performance.now();
		const dur = 1100;
		let raf = 0;
		const tick = (t: number) => {
			const p = Math.min(1, (t - start) / dur);
			const eased = 1 - Math.pow(1 - p, 3);
			shown = target * eased;
			if (p < 1) raf = requestAnimationFrame(tick);
		};
		raf = requestAnimationFrame(tick);
		return () => cancelAnimationFrame(raf);
	});

	const tone = $derived(rate >= 70 ? 'good' : rate >= 40 ? 'mid' : 'bad');
	const color = $derived(`var(--${tone})`);
	const offset = $derived(circ * (1 - shown / 100));
</script>

<div class="ring" style="width:{size}px; height:{size}px;">
	<svg viewBox="0 0 {size} {size}" width={size} height={size}>
		<circle cx={size / 2} cy={size / 2} {r} fill="none" stroke="var(--line)" stroke-width={stroke} />
		<circle
			cx={size / 2}
			cy={size / 2}
			{r}
			fill="none"
			stroke={color}
			stroke-width={stroke}
			stroke-linecap="round"
			stroke-dasharray={circ}
			stroke-dashoffset={offset}
			transform="rotate(-90 {size / 2} {size / 2})"
		/>
	</svg>
	<div class="center">
		<span class="value" style="color:{color};">{Math.round(shown)}<span class="pct">%</span></span>
		<span class="label">{label}</span>
	</div>
</div>

<style>
	.ring { position: relative; display: inline-grid; place-items: center; }
	.center {
		position: absolute;
		inset: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.1rem;
	}
	.value {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 2.6rem;
		line-height: 1;
		font-variant-numeric: tabular-nums;
		letter-spacing: -0.03em;
	}
	.pct { font-size: 1.2rem; margin-left: 1px; }
	.label {
		font-family: var(--font-mono);
		font-size: 0.66rem;
		letter-spacing: 0.16em;
		text-transform: uppercase;
		color: var(--ink-mute);
	}
</style>
