<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';

	let { children } = $props();

	let theme = $state<'light' | 'dark'>('light');
	let isScrolled = $state(false);

	$effect(() => {
		const current = document.documentElement.getAttribute('data-theme');
		theme = current === 'dark' ? 'dark' : 'light';
	});

	$effect(() => {
		function handleScroll() {
			isScrolled = window.scrollY > 0;
		}

		window.addEventListener('scroll', handleScroll, { passive: true });
		return () => window.removeEventListener('scroll', handleScroll);
	});

	function toggleTheme() {
		theme = theme === 'dark' ? 'light' : 'dark';
		document.documentElement.setAttribute('data-theme', theme);
		try {
			localStorage.setItem('signal-theme', theme);
		} catch (e) {
			/* ignore */
		}
	}

	const path = $derived($page.url.pathname);
</script>

<div class="shell">
	<header class="topbar" class:scrolled={isScrolled}>
		<div class="topbar-inner">
			<a href="/" class="brand" aria-label="Signal home">
				<span class="brand-mark" aria-hidden="true">
					<svg viewBox="0 0 32 32" width="26" height="26">
						<rect width="32" height="32" rx="8" fill="var(--accent)" />
						<path
							d="M9 17l4.5 4.5L23 11"
							stroke="#fbfdfc"
							stroke-width="3"
							fill="none"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
				</span>
				<span class="brand-name">Signal</span>
			</a>

			<nav class="nav" aria-label="Primary">
				<a href="/" class="nav-link" class:active={path === '/'}>Match</a>
				<a href="/history" class="nav-link" class:active={path.startsWith('/history')}>History</a>
			</nav>

			<button class="theme-toggle" onclick={toggleTheme} aria-label="Toggle color theme">
				{#if theme === 'dark'}
					<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>
				{:else}
					<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" /></svg>
				{/if}
			</button>
		</div>
	</header>

	<main class="content">
		{@render children()}
	</main>

	<footer class="footer">
		<span>Signal · AI skill-gap analysis</span>
		<span class="dot" aria-hidden="true">·</span>
		<span>Powered by Groq LLM</span>
	</footer>
</div>

<style>
	.shell {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.topbar {
		position: sticky;
		top: 0;
		z-index: 20;
		background: color-mix(in srgb, var(--paper) 82%, transparent);
		backdrop-filter: blur(8px) saturate(1.3);
		-webkit-backdrop-filter: blur(8px) saturate(1.3);
		border-bottom: 1px solid transparent;
		transition: backdrop-filter 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
	}

	.topbar.scrolled {
		background: color-mix(in srgb, var(--paper) 90%, transparent);
		backdrop-filter: blur(16px) saturate(1.5);
		-webkit-backdrop-filter: blur(16px) saturate(1.5);
		border-bottom: 1px solid var(--line);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
	}

	.topbar-inner {
		max-width: 74rem;
		margin: 0 auto;
		padding: 0 1.5rem;
		height: 62px;
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.brand {
		display: inline-flex;
		align-items: center;
		gap: 0.55rem;
		color: var(--ink);
	}
	.brand-mark { display: inline-flex; filter: drop-shadow(0 2px 5px var(--accent-ring)); }
	.brand-name {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 1.25rem;
		letter-spacing: -0.03em;
	}

	.nav {
		margin-left: auto;
		display: flex;
		gap: 0.25rem;
	}
	.nav-link {
		padding: 0.45rem 0.95rem;
		border-radius: 99px;
		font-weight: 600;
		font-size: 0.9rem;
		color: var(--ink-mute);
		transition: color 0.2s, background 0.2s;
	}
	.nav-link:hover { color: var(--ink); background: var(--card-hover); }
	.nav-link.active { color: var(--accent); background: var(--accent-soft); }

	.theme-toggle {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 38px;
		height: 38px;
		border-radius: 99px;
		border: 1px solid var(--line);
		background: var(--card);
		color: var(--ink-soft);
		cursor: pointer;
		transition: color 0.2s, border-color 0.2s, transform 0.2s;
	}
	.theme-toggle:hover { color: var(--accent); border-color: var(--accent); transform: rotate(-12deg); }

	.content {
		flex: 1;
		width: 100%;
		max-width: 74rem;
		margin: 0 auto;
		padding: 3rem 1.5rem 4rem;
	}

	.footer {
		border-top: 1px solid var(--line);
		padding: 1.25rem 1.5rem;
		display: flex;
		gap: 0.6rem;
		justify-content: center;
		align-items: center;
		font-size: 0.82rem;
		color: var(--ink-mute);
	}
	.dot { opacity: 0.5; }

	@media (max-width: 600px) {
		.content { padding: 2rem 1.1rem 3rem; }
		.brand-name { font-size: 1.1rem; }
	}
</style>
