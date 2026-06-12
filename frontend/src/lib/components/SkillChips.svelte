<script lang="ts">
	let {
		title,
		skills,
		variant = 'good'
	}: { title: string; skills: string[]; variant?: 'good' | 'bad' } = $props();
</script>

<div class="block">
	<div class="head">
		<span class="dot {variant}" aria-hidden="true"></span>
		<h4>{title}</h4>
		<span class="count">{skills.length}</span>
	</div>
	{#if skills.length}
		<div class="chips">
			{#each skills as s, i}
				<span class="chip chip-{variant} rise" style="animation-delay:{Math.min(i * 0.025, 0.5)}s;">
					{s}
				</span>
			{/each}
		</div>
	{:else}
		<p class="empty">None</p>
	{/if}
</div>

<style>
	.block { display: flex; flex-direction: column; gap: 0.85rem; }
	.head { display: flex; align-items: center; gap: 0.5rem; }
	.head h4 { font-size: 0.95rem; font-weight: 700; letter-spacing: -0.01em; }
	.dot { width: 8px; height: 8px; border-radius: 99px; }
	.dot.good { background: var(--good); }
	.dot.bad { background: var(--bad); }
	.count {
		margin-left: auto;
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--ink-mute);
	}
	.chips { display: flex; flex-wrap: wrap; gap: 0.45rem; }
	.empty { color: var(--ink-mute); font-size: 0.88rem; font-style: italic; }
</style>
