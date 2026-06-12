import logging
import sys

import config
from matcher import match_skills
from output import write_report
from parsers import read_document
from skill_extractor import extract_skills

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
)


def prompt_file(prompt: str) -> str:
    while True:
        path = input(prompt).strip()
        if not path:
            print("  [!] Path cannot be empty.")
            continue
        try:
            read_document(path)
            return path
        except FileNotFoundError:
            print(f"  [!] File not found: {path}")
        except ValueError as e:
            print(f"  [!] {e}")
        except Exception as e:
            print(f"  [!] Error reading file: {e}")


def main() -> None:
    if not config.LLM_API_KEY:
        print(
            "[!] LLM_API_KEY not set. Create a .env file with your Groq API key."
        )
        print("    Copy .env.example to .env and fill in your key.")
        sys.exit(1)

    print("=" * 48)
    print("  SKILLMATCHER v0.1")
    print("  Vault-Tec Engineering Terminal")
    print("=" * 48)
    print()

    session_count = 0

    while True:
        print("--- New Match ---")
        jd_path = prompt_file("  Job Description file path: ")
        resume_path = prompt_file("  Resume file path: ")
        print()

        jd_text = read_document(jd_path)
        resume_text = read_document(resume_path)

        print("  [*] Extracting skills from Job Description...")
        jd_skills = extract_skills(jd_text, "Job Description")
        print(f"      Found {len(jd_skills)} skills.")

        print("  [*] Extracting skills from Resume...")
        resume_skills = extract_skills(resume_text, "Resume")
        print(f"      Found {len(resume_skills)} skills.")

        print("  [*] Matching skills...")
        matched, missing = match_skills(jd_skills, resume_skills)
        total = len(matched) + len(missing)
        match_pct = (len(matched) / total * 100) if total > 0 else 0.0

        jd_name = jd_path.rsplit("/", 1)[-1]
        resume_name = resume_path.rsplit("/", 1)[-1]
        report_path = write_report(
            jd_name, resume_name, matched, missing, match_pct
        )

        print()
        print(f"  Match Rate: {len(matched)}/{total} ({match_pct:.1f}%)")
        print(f"  Report saved: {report_path}")
        print()

        session_count += 1

        again = input("  Process another resume? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            break
        print()

    print()
    print("=" * 48)
    print(f"  Session complete. {session_count} report(s) generated.")
    print("  Vault-Tec recommends: Keep your skills sharp!")
    print("=" * 48)


if __name__ == "__main__":
    main()
