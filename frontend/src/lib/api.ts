const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

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
	created_at: string;
}

export interface HistoryListResponse {
	items: HistoryItem[];
	total: number;
}

export async function matchSkills(
	jdFile: File,
	resumeFile: File
): Promise<MatchResult> {
	const form = new FormData();
	form.append('jd_file', jdFile);
	form.append('resume_file', resumeFile);

	const res = await fetch(`${API_BASE}/api/match`, {
		method: 'POST',
		body: form,
	});

	if (!res.ok) {
		const err = await res.json();
		throw new Error(err.detail ?? `Server error: ${res.status}`);
	}

	return res.json();
}

export async function getHistory(
	limit = 20,
	offset = 0
): Promise<HistoryListResponse> {
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
	const res = await fetch(`${API_BASE}/api/history/${id}`, {
		method: 'DELETE',
	});
	if (!res.ok) throw new Error('Failed to delete');
}

export function getReportUrl(filename: string): string {
	return `${API_BASE}/api/report/${filename}`;
}
