import { env } from '$env/dynamic/public';

// Read at runtime (not inlined at build) so a single Docker image can point at
// any backend via the PUBLIC_API_BASE environment variable.
const API_BASE = env.PUBLIC_API_BASE ?? 'http://localhost:8000';

export interface Recommendation {
	skill: string;
	why_it_matters: string;
	how_to_learn: string;
}

export interface GapAnalysis {
	verdict: string;
	summary: string;
	recommendations: Recommendation[];
}

export interface CategoryBreakdown {
	matched: string[];
	missing: string[];
}

export interface MatchResult {
	status: string;
	match_id: number | null;
	job_description: string;
	resume: string;
	matched: string[];
	missing: string[];
	total_jd_skills: number;
	total_resume_skills: number;
	match_rate: number;
	report_url: string | null;
	categories: Record<string, CategoryBreakdown>;
	analysis: GapAnalysis;
}

export interface BatchMatchResult {
	status: string;
	job_description: string;
	items: MatchResult[];
}

export interface HistoryItem {
	id: number;
	jd_filename: string;
	resume_filename: string;
	matched_skills: string[];
	missing_skills: string[];
	total_jd: number;
	total_resume: number;
	match_rate: number;
	report_filename: string;
	categories: Record<string, CategoryBreakdown>;
	recommendations: GapAnalysis | Record<string, never>;
	created_at: string;
}

export interface HistoryListResponse {
	items: HistoryItem[];
	total: number;
}

/** One side of a match: either an uploaded file or pasted text. */
export type Source = { file: File } | { text: string };

function appendSource(form: FormData, fileKey: string, textKey: string, src: Source) {
	if ('file' in src) form.append(fileKey, src.file);
	else form.append(textKey, src.text);
}

async function parseError(res: Response): Promise<never> {
	let detail = `Server error: ${res.status}`;
	try {
		const err = await res.json();
		detail = err.detail ?? detail;
	} catch {
		/* non-JSON error body */
	}
	throw new Error(detail);
}

export async function matchSkills(jd: Source, resume: Source): Promise<MatchResult> {
	const form = new FormData();
	appendSource(form, 'jd_file', 'jd_text', jd);
	appendSource(form, 'resume_file', 'resume_text', resume);

	const res = await fetch(`${API_BASE}/api/match`, { method: 'POST', body: form });
	if (!res.ok) await parseError(res);
	return res.json();
}

export async function matchBatch(jd: Source, resumes: File[]): Promise<BatchMatchResult> {
	const form = new FormData();
	appendSource(form, 'jd_file', 'jd_text', jd);
	for (const f of resumes) form.append('resume_files', f);

	const res = await fetch(`${API_BASE}/api/match/batch`, { method: 'POST', body: form });
	if (!res.ok) await parseError(res);
	return res.json();
}

export async function getHistory(limit = 20, offset = 0): Promise<HistoryListResponse> {
	const res = await fetch(`${API_BASE}/api/history?limit=${limit}&offset=${offset}`);
	if (!res.ok) throw new Error('Failed to fetch history');
	return res.json();
}

export async function getHistoryItem(id: number): Promise<HistoryItem> {
	const res = await fetch(`${API_BASE}/api/history/${id}`);
	if (!res.ok) throw new Error('Match not found');
	return res.json();
}

export async function deleteHistoryItem(id: number): Promise<void> {
	const res = await fetch(`${API_BASE}/api/history/${id}`, { method: 'DELETE' });
	if (!res.ok) throw new Error('Failed to delete');
}

export function getReportUrl(filename: string, format: 'txt' | 'json' = 'txt'): string {
	return `${API_BASE}/api/report/${filename}?format=${format}`;
}
