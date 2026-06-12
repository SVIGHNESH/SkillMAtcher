<script lang="ts">
	import FileDropZone from './FileDropZone.svelte';

	let {
		label,
		placeholder = 'Paste text here…',
		file = $bindable<File | null>(null),
		text = $bindable(''),
		method = $bindable<'upload' | 'paste'>('upload')
	}: {
		label: string;
		placeholder?: string;
		file?: File | null;
		text?: string;
		method?: 'upload' | 'paste';
	} = $props();

	function setMethod(m: 'upload' | 'paste') {
		method = m;
	}
</script>

<div class="source">
	<div class="tabs" role="tablist" aria-label="{label} input method">
		<button
			role="tab"
			aria-selected={method === 'upload'}
			class="tab"
			class:active={method === 'upload'}
			onclick={() => setMethod('upload')}>Upload</button
		>
		<button
			role="tab"
			aria-selected={method === 'paste'}
			class="tab"
			class:active={method === 'paste'}
			onclick={() => setMethod('paste')}>Paste text</button
		>
	</div>

	{#if method === 'upload'}
		<FileDropZone {label} bind:file />
	{:else}
		<div class="paste">
			<span class="plabel">{label}</span>
			<textarea bind:value={text} {placeholder} rows="7" spellcheck="false"></textarea>
		</div>
	{/if}
</div>

<style>
	.source { display: flex; flex-direction: column; gap: 0.7rem; }
	.tabs {
		display: inline-flex;
		gap: 0.2rem;
		padding: 0.2rem;
		background: var(--paper-2);
		border: 1px solid var(--line);
		border-radius: 99px;
		align-self: flex-start;
	}
	.tab {
		font-family: var(--font-body);
		font-weight: 600;
		font-size: 0.8rem;
		padding: 0.32rem 0.85rem;
		border: none;
		background: transparent;
		color: var(--ink-mute);
		border-radius: 99px;
		cursor: pointer;
		transition: color 0.2s, background 0.2s;
	}
	.tab:hover { color: var(--ink); }
	.tab.active { background: var(--card); color: var(--accent); box-shadow: var(--shadow-sm); }

	.paste { display: flex; flex-direction: column; gap: 0.5rem; }
	.plabel { font-weight: 700; font-size: 0.95rem; }
	textarea {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		line-height: 1.5;
		padding: 1rem;
		border: 1.5px solid var(--line-strong);
		border-radius: var(--radius);
		background: var(--card);
		color: var(--ink);
		resize: vertical;
		min-height: 168px;
		transition: border-color 0.2s, box-shadow 0.2s;
	}
	textarea:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-ring); }
</style>
