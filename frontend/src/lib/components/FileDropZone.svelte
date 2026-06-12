<script lang="ts">
	let {
		label = 'DATA_DISK.TXT',
		accept = '.txt,.pdf,.docx',
		onFile,
		style = ''
	}: {
		label?: string;
		accept?: string;
		onFile: (file: File) => void;
		style?: string;
	} = $props();

	let file = $state<File | null>(null);
	let dragOver = $state(false);
	const inputId = `file-${label.replace(/\s+/g, '-').toLowerCase()}`;

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		dragOver = false;
		const f = e.dataTransfer?.files?.[0];
		if (f) { file = f; onFile(f); }
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		dragOver = true;
	}

	function handleDragLeave() { dragOver = false; }

	function handleFilePick(e: Event) {
		const input = e.target as HTMLInputElement;
		const f = input.files?.[0];
		if (f) { file = f; onFile(f); }
	}

	function handleClick() {
		document.getElementById(inputId)?.click();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			handleClick();
		}
	}
</script>

<div
	class="drop-zone {file ? 'has-file' : ''} {dragOver ? 'drag-over' : ''}"
	role="button"
	tabindex="0"
	onclick={handleClick}
	ondragover={handleDragOver}
	ondragleave={handleDragLeave}
	ondrop={handleDrop}
	onkeydown={handleKeydown}
	style={style}
>
	<input
		id={inputId}
		type="file"
		accept={accept}
		class="hidden"
		onchange={handleFilePick}
	/>

	<div class="bracket-tl"></div><div class="bracket-tr"></div>
	<div class="bracket-bl"></div><div class="bracket-br"></div>

	<div class="inner-content">
		{#if file}
			<div><span class="prompt"></span> {label}</div>
			<div class="file-name">> {file.name.toUpperCase()}</div>
			<div class="text-dim">  SIZE: {(file.size / 1024).toFixed(1)} KB</div>
			<div class="text-dim">  STATUS: LOADED [OK]</div>
			<br/>
			<div class="text-dim">  [ CLICK TO REPLACE ]</div>
		{:else}
			<div><span class="prompt"></span> {label}</div>
			<div class="text-dim">  STATUS: AWAITING INPUT...</div>
			<div class="text-dim">  FORMATS: TXT, PDF, DOCX</div>
			<br/>
			<div class="blink-text">  [ CLICK OR DRAG TO INSERT ]</div>
		{/if}
	</div>
</div>

<style>
	.drop-zone {
		position: relative;
		padding: 24px;
		cursor: pointer;
		min-height: 180px;
		background: rgba(0, 0, 0, 0.4);
		transition: background 0.2s;
	}

	.drop-zone:hover, .drop-zone.drag-over {
		background: rgba(57, 255, 20, 0.1);
	}

	.drop-zone.has-file {
		background: rgba(0, 0, 0, 0.8);
	}

	.hidden {
		display: none;
	}

	.inner-content {
		position: relative;
		z-index: 2;
	}

	.file-name {
		color: var(--phosphor-primary);
		text-shadow: 0 0 8px var(--phosphor-primary);
	}

	.blink-text {
		animation: blink 2s step-end infinite;
	}

	/* Corner Brackets */
	.bracket-tl, .bracket-tr, .bracket-bl, .bracket-br {
		position: absolute;
		width: 16px;
		height: 16px;
		border-color: var(--phosphor-dim);
		border-style: solid;
		transition: border-color 0.2s;
	}

	.drop-zone:hover .bracket-tl,
	.drop-zone:hover .bracket-tr,
	.drop-zone:hover .bracket-bl,
	.drop-zone:hover .bracket-br,
	.drop-zone.has-file .bracket-tl,
	.drop-zone.has-file .bracket-tr,
	.drop-zone.has-file .bracket-bl,
	.drop-zone.has-file .bracket-br {
		border-color: var(--phosphor-primary);
	}

	.bracket-tl { top: 0; left: 0; border-width: 2px 0 0 2px; }
	.bracket-tr { top: 0; right: 0; border-width: 2px 2px 0 0; }
	.bracket-bl { bottom: 0; left: 0; border-width: 0 0 2px 2px; }
	.bracket-br { bottom: 0; right: 0; border-width: 0 2px 2px 0; }
</style>
