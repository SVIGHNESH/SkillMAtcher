<script lang="ts">
	import '../app.css';

	let { children } = $props();
</script>

<div class="app-shell">
	<nav class="topbar">
		<div class="topbar-inner">
			<a href="/" class="logo">
				<span class="logo-prompt">$</span>
				<span class="logo-text">skillmatcher</span>
				<span class="logo-cursor">_</span>
			</a>
			<div class="topbar-links">
				<a href="/" class="nav-link">match</a>
				<a href="/history" class="nav-link">history</a>
			</div>
		</div>
	</nav>

	<main class="main-content">
		{@render children()}
	</main>

	<div class="status-bar">
		<span class="status-item">
			<span class="status-dot"></span>
			console v0.1
		</span>
		<span class="status-item">groq llm engine</span>
		<span class="status-item">reports: ./output/</span>
	</div>
</div>

<style>
	.app-shell {
		position: relative;
		z-index: 1;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.topbar {
		border-bottom: 1px solid var(--border);
		background: rgba(7, 8, 15, 0.85);
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
		position: sticky;
		top: 0;
		z-index: 10;
	}

	.topbar-inner {
		max-width: 72rem;
		margin: 0 auto;
		padding: 0 1.5rem;
		height: 52px;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.3rem;
		text-decoration: none;
		font-family: var(--font-mono);
		font-size: 0.95rem;
	}

	.logo-prompt {
		color: var(--accent);
		font-weight: 700;
	}

	.logo-text {
		color: var(--text-primary);
		font-weight: 500;
		letter-spacing: 0.03em;
	}

	.logo-cursor {
		color: var(--accent);
		font-weight: 700;
		animation: cursorBlink 1s step-end infinite;
	}

	.topbar-links {
		display: flex;
		gap: 0.25rem;
	}

	.nav-link {
		padding: 0.4rem 0.9rem;
		border-radius: 6px;
		font-family: var(--font-heading);
		font-size: 0.78rem;
		font-weight: 500;
		color: var(--text-muted);
		text-decoration: none;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		transition: all 0.2s;
	}

	.nav-link:hover {
		color: var(--accent);
		background: var(--accent-glow);
	}

	:global(.nav-link.active) {
		color: var(--accent);
		background: var(--accent-glow);
	}

	.main-content {
		flex: 1;
		width: 100%;
		max-width: 72rem;
		margin: 0 auto;
		padding: 2.5rem 1.5rem;
	}

	.status-bar {
		border-top: 1px solid var(--border);
		background: rgba(7, 8, 15, 0.9);
		padding: 0.5rem 1.5rem;
		display: flex;
		gap: 1.5rem;
		font-size: 0.65rem;
		font-family: var(--font-mono);
		color: var(--text-dim);
		justify-content: center;
		flex-wrap: wrap;
	}

	.status-item {
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}

	.status-dot {
		width: 5px;
		height: 5px;
		border-radius: 50%;
		background: var(--success);
		box-shadow: 0 0 6px var(--success);
	}

	@media (max-width: 640px) {
		.main-content { padding: 1.5rem 1rem; }
	}
</style>
