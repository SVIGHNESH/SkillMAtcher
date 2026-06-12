<script lang="ts">
	let {
		label = 'Document',
		hint = 'TXT, PDF or DOCX',
		accept = '.txt,.pdf,.docx',
		file = $bindable<File | null>(null),
		onFile
	}: {
		label?: string;
		hint?: string;
		accept?: string;
		file?: File | null;
		onFile?: (file: File) => void;
	} = $props();

	let dragOver = $state(false);
	const inputId = $derived(`file-${label.replace(/\s+/g, '-').toLowerCase()}`);

	function set(f: File | undefined) {
		if (f) {
			file = f;
			onFile?.(f);
		}
	}
	function onDrop(e: DragEvent) {
		e.preventDefault();
		dragOver = false;
		set(e.dataTransfer?.files?.[0]);
	}
	function onPick(e: Event) {
		set((e.target as HTMLInputElement).files?.[0]);
	}
	function open() {
		document.getElementById(inputId)?.click();
	}
	function onKey(e: KeyboardEvent) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			open();
		}
	}
</script>

<div
	class="drop"
	class:has={file}
	class:over={dragOver}
	role="button"
	tabindex="0"
	aria-label="{label}: choose a file"
	onclick={open}
	onkeydown={onKey}
	ondragover={(e) => {
		e.preventDefault();
		dragOver = true;
	}}
	ondragleave={() => (dragOver = false)}
	ondrop={onDrop}
>
	<input id={inputId} type="file" {accept} class="sr" onchange={onPick} />

	<div class="top">
		<span class="label">{label}</span>
		{#if file}<span class="ok">✓ Loaded</span>{/if}
	</div>

	{#if file}
		<div class="file">
			<span class="fname">{file.name}</span>
			<span class="fsize">{(file.size / 1024).toFixed(1)} KB · click to replace</span>
		</div>
	{:else}
		<div class="empty">
			<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
				<path d="M12 16V4M12 4l-4 4M12 4l4 4" />
				<path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
			</svg>
			<span class="cta">Drop file or <u>browse</u></span>
			<span class="hint">{hint}</span>
		</div>
	{/if}
</div>

<style>
	.drop {
		position: relative;
		display: flex;
		flex-direction: column;
		gap: 0.7rem;
		padding: 1.5rem;
		min-height: 168px;
		border: 1.5px dashed var(--line-strong);
		border-radius: var(--radius);
		background: var(--card);
		cursor: pointer;
		transition: border-color 0.2s, background 0.2s, transform 0.15s;
	}
	.drop:hover, .drop.over { border-color: var(--accent); background: var(--accent-soft); }
	.drop.over { transform: scale(1.01); }
	.drop.has { border-style: solid; border-color: var(--line-strong); background: var(--card); }
	.drop:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--accent-ring); }
	.sr { position: absolute; width: 1px; height: 1px; opacity: 0; pointer-events: none; }

	.top { display: flex; align-items: center; justify-content: space-between; }
	.label { font-weight: 700; font-size: 0.95rem; }
	.ok { font-family: var(--font-mono); font-size: 0.72rem; color: var(--good); }

	.empty {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.45rem;
		color: var(--ink-mute);
		text-align: center;
	}
	.cta { font-weight: 500; color: var(--ink-soft); font-size: 0.92rem; }
	.cta u { color: var(--accent); text-decoration-thickness: 2px; text-underline-offset: 2px; }
	.hint { font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.05em; }

	.file { display: flex; flex-direction: column; gap: 0.25rem; justify-content: center; flex: 1; }
	.fname { font-weight: 600; word-break: break-all; }
	.fsize { font-family: var(--font-mono); font-size: 0.72rem; color: var(--ink-mute); }
</style>
