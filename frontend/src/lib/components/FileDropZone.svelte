<script lang="ts">
	let {
		label = 'Drop file here',
		accept = '.txt,.pdf,.docx',
		icon = '[]',
		onFile,
		style = ''
	}: {
		label?: string;
		accept?: string;
		icon?: string;
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

	{#if file}
		<div class="drop-zone-icon" style="font-size:1.4rem; margin-bottom:0.5rem;">{icon}</div>
		<div class="drop-zone-filename">{file.name}</div>
		<div class="status-line" style="font-size:0.68rem; margin-top:0.35rem;">
			<span class="success-text">loaded</span> &mdash; {(file.size / 1024).toFixed(1)} KB
		</div>
		<div class="drop-zone-sub">drop to replace</div>
	{:else}
		<div class="drop-zone-icon">{icon}</div>
		<div class="drop-zone-label">{label}</div>
		<div class="drop-zone-sub">drag &amp; drop &bull; click to browse</div>
		<div class="drop-zone-sub" style="margin-top:0.15rem;">.txt &bull; .pdf &bull; .docx</div>
	{/if}
</div>
