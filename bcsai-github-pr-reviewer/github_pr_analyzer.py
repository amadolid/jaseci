"""GitHub PR Analyzer: Analyzes pull requests using AI, posts review comments, and manages approvals."""  # noqa: E501

import base64
import logging
import os
import re
import uuid
from collections.abc import Iterable
from difflib import unified_diff
from functools import cache
from re import DOTALL, compile
from typing import Any, Iterator, Tuple

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
COMMAND = os.getenv("COMMAND", "pr-review")
CODE_REVIEW_API_ENDPOINT = os.getenv("CODE_REVIEW_API_ENDPOINT")
PROVIDER = os.getenv("PROVIDER", "openai")
AUTO_APPROVE_CLEAN_PRS = os.getenv("AUTO_APPROVE_CLEAN_PRS", "true").lower() == "true"

# Sync PR Detection - Single constant for team to use
SYNC_PR_KEYWORD = os.getenv("SYNC_PR_KEYWORD", "[SYNC]")

CHANGE_TYPES = ("added", "modified")
HUNK_HEADER_PATTERN = compile(r"@@ -(\d+),(\d+) \+(\d+),(\d+) @@(.*)")
TASK_EXEC_PATTERN = compile(r"<task_execution>(.*?)</task_execution>", DOTALL)
PROG_LANGS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".java": "Java",
    ".cs": "C#",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".html": "HTML",
    ".htm": "HTML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".xml": "XML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "SCSS",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".swift": "Swift",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cpp": "C++",
    ".cxx": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C",
    ".hpp": "C++",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".sql": "SQL",
    ".r": "R",
    ".scala": "Scala",
    ".pl": "Perl",
    ".dart": "Dart",
}

# Environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_REPOSITORY_ID = os.getenv("GITHUB_REPOSITORY_ID")
GITHUB_REF_NAME = os.getenv("GITHUB_REF_NAME")
GITHUB_HEAD_REF = os.getenv("GITHUB_HEAD_REF")
PR_NUMBER = os.getenv("GITHUB_PR_NUMBER")

if not GITHUB_TOKEN:
    raise ValueError("Missing GITHUB_TOKEN in environment variables")

if not GITHUB_REPOSITORY:
    raise ValueError("Missing GITHUB_REPOSITORY in environment variables")

# Parse repository info
GIT_OWNER, GIT_REPOSITORY_NAME = GITHUB_REPOSITORY.split("/")

# Get PR number from various sources
if not PR_NUMBER:
    if GITHUB_REF_NAME:
        # For pull requests, GITHUB_REF_NAME is like "123/merge"
        if "/" in GITHUB_REF_NAME:
            potential_pr = GITHUB_REF_NAME.split("/")[0]
            if potential_pr.isdigit():
                PR_NUMBER = potential_pr
        elif GITHUB_REF_NAME.isdigit():
            PR_NUMBER = GITHUB_REF_NAME
    if not PR_NUMBER and GITHUB_HEAD_REF:
        # Try to extract PR number from head ref if it's in format like "pr-123"
        match = re.search(r"pr-(\d+)", GITHUB_HEAD_REF)
        if match:
            PR_NUMBER = match.group(1)

if not PR_NUMBER:
    raise ValueError("Could not determine PR number from environment variables")


def get_repository_uuid() -> str:
    """Generate a UUID for the repository based on GitHub repository ID."""
    if GITHUB_REPOSITORY_ID:
        # Create a deterministic UUID from the repository ID
        namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace
        return str(uuid.uuid5(namespace, GITHUB_REPOSITORY_ID))
    else:
        # Fallback to a default UUID if no repository ID is available
        return "550e8400-e29b-41d4-a716-446655440000"


@cache
def get_auth_headers() -> dict[str, str]:
    """Get authorization headers for GitHub API."""
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


def github_get(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Make GET request to GitHub API."""
    response = requests.get(url, headers=get_auth_headers(), params=params)
    response.raise_for_status()
    return response.json()


def github_post(url: str, json_data: dict[str, Any]) -> dict[str, Any]:
    """Make POST request to GitHub API."""
    response = requests.post(url, headers=get_auth_headers(), json=json_data)
    response.raise_for_status()
    return response.json()


def get_changed_files(pr_number: str) -> Iterable[str]:
    """Get list of changed files in a pull request."""
    try:
        url = f"https://api.github.com/repos/{GIT_OWNER}/{GIT_REPOSITORY_NAME}/pulls/{pr_number}/files"  # noqa: E501
        files_data = github_get(url)

        changed_files = set()
        for file_info in files_data:
            if file_info["status"] in CHANGE_TYPES:
                changed_files.add(file_info["filename"])

        logger.info(f"Total changed files: {len(changed_files)}")
        return changed_files
    except Exception as e:
        logger.error(f"Error getting changed files for PR {pr_number}: {e}")
        raise


def get_latest_two_commits(pr_number: str) -> Tuple[str | None, str | None]:
    """Get the latest two commits from the PR head branch."""
    try:
        url = (
            f"https://api.github.com/repos/{GIT_OWNER}/"
            f"{GIT_REPOSITORY_NAME}/pulls/{pr_number}/commits"
        )
        commits = github_get(url)
        if len(commits) >= 2:
            return commits[-1]["sha"], commits[-2]["sha"]
        elif len(commits) == 1:
            return commits[0]["sha"], None
        return None, None
    except Exception as e:
        logger.error(f"Error getting commits for PR {pr_number}: {e}")
        return None, None


def get_file_diff_by_commit(
    file_path: str, base_ref: str, head_ref: str, pr_number: str
) -> Tuple[str | None, str]:
    """Generate diff based on the last two commits on the head branch."""
    logger.info(f"Generating commit-based diff for {file_path}.")

    head_commit, prev_commit = get_latest_two_commits(pr_number)
    base_content = ""

    if prev_commit:
        base_content = get_file_contents(file_path, prev_commit)

    if not base_content:
        logger.warning(
            f"Could not get content from previous commit for {file_path}. "
            "Falling back to base branch."
        )
        base_content = get_file_contents(file_path, base_ref)

    head_content = get_file_contents(file_path, head_ref)
    if not head_content:
        logger.warning(f"Could not get head content for {file_path}.")
        return None, base_content

    diff_lines = list(
        unified_diff(
            base_content.splitlines(keepends=True),
            head_content.splitlines(keepends=True),
        )
    )
    return "\n".join(diff_lines) if diff_lines else None, base_content


def get_file_diff_by_branch(
    file_path: str, base_ref: str, head_ref: str
) -> Tuple[str | None, str]:
    """Generate diff based purely on base and head branches."""
    logger.info(
        f"Generating branch-based diff for {file_path} "
        f"between '{base_ref}' and '{head_ref}'."
    )

    base_content = get_file_contents(file_path, base_ref)
    head_content = get_file_contents(file_path, head_ref)

    if not base_content and not head_content:
        logger.warning(f"Could not get any content for {file_path}. Skipping diff.")
        return None, ""

    diff_lines = list(
        unified_diff(
            base_content.splitlines(keepends=True),
            head_content.splitlines(keepends=True),
        )
    )
    return "\n".join(diff_lines) if diff_lines else None, base_content


def get_file_contents(file_path: str, ref: str = None) -> str:
    """Get file contents from GitHub repository."""
    try:
        url = f"https://api.github.com/repos/{GIT_OWNER}/{GIT_REPOSITORY_NAME}/contents/{file_path}"  # noqa: E501
        params = {}
        if ref:
            params["ref"] = ref

        response = requests.get(url, headers=get_auth_headers(), params=params)
        if response.ok:
            file_data = response.json()
            return base64.b64decode(file_data["content"]).decode(
                "utf-8", errors="ignore"
            )
        logger.warning(f"Failed to download {file_path}: {response.status_code}")
        return ""
    except Exception as e:
        logger.warning(f"Could not fetch {file_path} from {ref}: {e}")
        return ""


def get_pr_details(pr_number: str) -> dict[str, Any]:
    """Get pull request details."""
    try:
        url = f"https://api.github.com/repos/{GIT_OWNER}/{GIT_REPOSITORY_NAME}/pulls/{pr_number}"  # noqa: E501
        return github_get(url)
    except Exception as e:
        logger.error(f"Error getting PR details for {pr_number}: {e}")
        raise


def get_file_diff(
    file_path: str, base_ref: str, head_ref: str
) -> Tuple[str | None, str]:
    """Generate diff between base and head for a file."""
    logger.info(f"Generating diff for {file_path} between {base_ref} and {head_ref}")

    base_content = get_file_contents(file_path, base_ref)
    head_content = get_file_contents(file_path, head_ref)

    if not base_content and not head_content:
        logger.warning(f"Could not get any content for {file_path}. Skipping diff.")
        return None, ""

    diff_lines = list(
        unified_diff(
            base_content.splitlines(keepends=True),
            head_content.splitlines(keepends=True),
        )
    )
    return "\n".join(diff_lines) if diff_lines else None, base_content


def split_diff_into_hunks(diff_text: str) -> list[str]:
    """Split a full diff text into a list of individual hunk strings."""
    if not diff_text:
        return []
    lines = diff_text.split("\n")
    hunks, current_hunk = [], []
    for line in lines[2:]:  # Skip unified_diff header
        if line.startswith("@@"):
            if current_hunk:
                hunks.append("\n".join(current_hunk))
            current_hunk = [line]
        elif current_hunk:
            current_hunk.append(line)
    if current_hunk:
        hunks.append("\n".join(current_hunk))
    return hunks


def extract_task_execution(text: str) -> str:
    """Extract content from <task_execution> tags or return original text."""
    if match := TASK_EXEC_PATTERN.search(text):
        return match.group(1).strip()
    return text.strip()


def post_review_comment(
    pr_number: str, file_path: str, start_line: int, end_line: int, comment: str
) -> None:
    """Post a review comment to a specific line in a PR."""
    try:
        # Get the PR details to get the commit SHA
        pr_details = get_pr_details(pr_number)
        commit_sha = pr_details["head"]["sha"]

        url = f"https://api.github.com/repos/{GIT_OWNER}/{GIT_REPOSITORY_NAME}/pulls/{pr_number}/comments"  # noqa: E501
        payload = {
            "body": comment,
            "commit_id": commit_sha,
            "path": file_path,
            "start_line": start_line,
            "start_side": "RIGHT",
            "line": end_line,
            "side": "RIGHT",
        }
        logger.info(f"Posting review comment on {file_path} at line {start_line}")
        github_post(url, payload)
    except Exception as e:
        logger.error(
            f"Failed to post review comment on PR {pr_number} for {file_path} at line {start_line}: {e}"  # noqa: E501
        )


def post_pr_comment(pr_number: str, comment: str) -> None:
    """Post a general comment to the PR."""
    try:
        url = f"https://api.github.com/repos/{GIT_OWNER}/{GIT_REPOSITORY_NAME}/issues/{pr_number}/comments"  # noqa: E501
        payload = {"body": comment}
        github_post(url, payload)
        logger.info(f"Posted general comment to PR {pr_number}")
    except Exception as e:
        logger.error(f"Failed to post comment to PR {pr_number}: {e}")


def is_sync_pr(pr_number: str) -> bool:
    """Detect if PR is a sync PR and should skip review."""
    try:
        pr_details = get_pr_details(pr_number)
        pr_title = pr_details.get("title", "")

        if SYNC_PR_KEYWORD.lower() in pr_title.lower():
            logger.info(
                f"Sync PR detected: title '{pr_title}' contains '{SYNC_PR_KEYWORD}'"
            )
            return True

        logger.debug(
            f"Not a sync PR: title '{pr_title}' does not contain '{SYNC_PR_KEYWORD}'"
        )
        return False
    except Exception as e:
        logger.warning(f"Error checking if PR is sync PR: {e}. Proceeding with review.")
        return False


def approve_pull_request(pr_number: str) -> None:
    """Approve a pull request."""
    try:
        url = f"https://api.github.com/repos/{GIT_OWNER}/{GIT_REPOSITORY_NAME}/pulls/{pr_number}/reviews"  # noqa: E501
        payload = {
            "event": "APPROVE",
            "body": "✅ Automatically approved by BCSAI Assist - No issues found in code review.",  # noqa: E501
        }
        github_post(url, payload)
        logger.info(f"Successfully approved PR #{pr_number} ✅")
    except Exception as e:
        logger.error(f"Failed to auto-approve PR: {e}")


def get_language_name(filename: str) -> str | None:
    """Detect programming language from file extension."""
    if "." in filename:
        ext = "." + filename.split(".")[-1]
        return PROG_LANGS.get(ext)
    return None


def check_existing_pr_review(repository_name: str, pull_request_id: str) -> bool:
    """Check if a PR review already exists via an external API."""
    if not CODE_REVIEW_API_ENDPOINT:
        logger.warning("CODE_REVIEW_API_ENDPOINT not set. Assuming no review exists.")
        return False

    api_key = os.getenv("CODE_REVIEW_API_KEY")
    if not api_key:
        logger.warning("CODE_REVIEW_API_KEY not set. Cannot authenticate with API.")
        return False

    try:
        repo_uuid = get_repository_uuid()
        url = f"{CODE_REVIEW_API_ENDPOINT}?repository_id={repo_uuid}&pull_request_id={pull_request_id}"  # noqa: E501
        logger.info(f"Checking for existing review at: {url}")
        api_headers = {"accept": "application/json", "X-API-KEY": api_key}
        resp = requests.get(url, headers=api_headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("data"):
            logger.info("An existing review was found in the database.")
            return True
        else:
            logger.info("No existing review found. A new review will be generated.")
            return False
    except Exception as e:
        logger.error(
            f"API check for existing PR review failed: {e}. Proceeding with review."
        )
        return False


def generate_bulk_review(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Post a review request and stream the response, yielding feedback for each hunk."""  # noqa: E501
    if not CODE_REVIEW_API_ENDPOINT:
        raise ValueError("CODE_REVIEW_API_ENDPOINT not configured")

    api_key = os.getenv("CODE_REVIEW_API_KEY")
    if not api_key:
        logger.error("CODE_REVIEW_API_KEY not set. Cannot authenticate with API.")
        return iter([])

    try:
        logger.info(f"Sending bulk review request to: {CODE_REVIEW_API_ENDPOINT}")
        logger.debug(f"Payload: {payload}")
        api_headers = {"Content-Type": "application/json", "X-API-KEY": api_key}
        response = requests.post(
            CODE_REVIEW_API_ENDPOINT,
            json=payload,
            headers=api_headers,
            timeout=600,
            stream=True,
        )

        if not response.ok:
            logger.error(
                f"API request failed with status {response.status_code}: {response.text}"  # noqa: E501
            )
            response.raise_for_status()

        for chunk in response.iter_lines():
            if chunk:  # filter out keep-alive new lines
                try:
                    # Try to parse as JSON - if it's streaming JSON lines
                    import orjson

                    yield orjson.loads(chunk)
                except Exception as e:
                    logger.warning(
                        f"Failed to parse a streaming chunk: {chunk}. Error: {e}"
                    )
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error during code review request: {e}")
        if hasattr(e.response, "text"):
            logger.error(f"Response body: {e.response.text}")
        return iter([])
    except Exception as e:
        logger.error(f"Error during streaming code review request: {e}")
        return iter([])


def github_pr_ai_analyzer(pr_number: str) -> None:
    """Analyze GitHub PR and generate AI reviews."""
    logger.info(f"Starting AI analysis for GitHub PR {pr_number}")
    try:
        # Check if this is a sync PR that should skip review
        if is_sync_pr(pr_number):
            logger.info(f"Skipping review for sync PR {pr_number}. Auto-approving...")
            if AUTO_APPROVE_CLEAN_PRS:
                approve_pull_request(pr_number)
            return

        # Get PR details
        pr_details = get_pr_details(pr_number)
        base_ref = pr_details["base"]["ref"]
        head_ref = pr_details["head"]["ref"]
        head_sha = pr_details["head"]["sha"]

        logger.info(f"Analyzing PR from {head_ref} to {base_ref}")

        # Check for existing review to determine diff strategy (smart review logic)
        review_exists = check_existing_pr_review(GITHUB_REPOSITORY, pr_number)
        use_commit_based = review_exists and head_sha
        diff_strategy = "commit-based" if use_commit_based else "branch-based"
        logger.info(f"Review exists: {review_exists}. Using {diff_strategy} diff.")

        # Get changed files
        changed_files = get_changed_files(pr_number)
        if not changed_files:
            logger.info("No changed files found. Approving clean PR.")
            if AUTO_APPROVE_CLEAN_PRS:
                approve_pull_request(pr_number)
            return

        changes_payload = []
        for file_path in changed_files:
            logger.info(f"Processing file: {file_path}")
            language = get_language_name(file_path)
            if not language:
                logger.info(f"Language not supported for {file_path}, skipping.")
                continue

            # Smart diff strategy: commit vs branch-based
            if use_commit_based:
                diff_content, base_content = get_file_diff_by_commit(
                    file_path, base_ref, head_ref, pr_number
                )
            else:
                diff_content, base_content = get_file_diff_by_branch(
                    file_path, base_ref, head_ref
                )
            if not diff_content:
                logger.info(f"No differences found for {file_path}, skipping.")
                continue

            hunks = split_diff_into_hunks(diff_content)
            if not hunks:
                logger.info(f"Could not parse hunks for {file_path}, skipping.")
                continue

            changes_payload.append(
                {
                    "file": file_path,
                    "language": language,
                    "source": base_content,
                    "hunks": hunks,
                }
            )

        if not changes_payload:
            logger.info("No processable changes found. Approving clean PR.")
            if AUTO_APPROVE_CLEAN_PRS:
                approve_pull_request(pr_number)
            return

        bulk_request_payload = {
            "repository_id": get_repository_uuid(),
            "repository_name": GITHUB_REPOSITORY,
            "pull_request_id": int(pr_number),
            "commit_id": head_sha,
            "changes": changes_payload,
            "provider": PROVIDER,
            "command": COMMAND,
            "metadata": {},
        }

        # Validate payload before sending
        if not head_sha:
            logger.error("Missing commit_id (head_sha) for bulk review request")
            return

        if not changes_payload:
            logger.warning("No changes to review - empty changes_payload")
            if AUTO_APPROVE_CLEAN_PRS:
                approve_pull_request(pr_number)
            return

        logger.info(f"Sending review request with {len(changes_payload)} changed files")

        comment_count = 0
        for hunk_feedback in generate_bulk_review(bulk_request_payload):
            file_path = hunk_feedback.get("file")
            comment_text = extract_task_execution(hunk_feedback.get("feedback", ""))
            hunk_header_line = hunk_feedback.get("hunk", "").split("\n", 1)[0]

            if not all([file_path, comment_text.strip(), hunk_header_line]):
                logger.warning(f"Skipping incomplete chunk: {hunk_feedback}")
                continue

            if "No significant issues" in comment_text:
                logger.info(f"Skipping non-issue comment for {file_path}.")
                continue

            if match := HUNK_HEADER_PATTERN.match(hunk_header_line):
                line_number = int(match.group(3))
                number_of_lines = line_number + int(match.group(4))
                print(hunk_header_line)
                print(line_number)
                print(number_of_lines)
                post_review_comment(
                    pr_number, file_path, line_number, number_of_lines, comment_text
                )
                comment_count += 1
            else:
                logger.warning(
                    f"Could not parse hunk header for comment in {file_path}: {hunk_header_line}"  # noqa: E501
                )

        logger.info(f"Analysis complete. Posted {comment_count} comments.")

        if comment_count == 0 and AUTO_APPROVE_CLEAN_PRS:
            logger.info("No issues found. Automatically approving PR.")
            approve_pull_request(pr_number)
        elif comment_count == 0:
            logger.info("No issues found. Auto-approval is disabled.")
        else:
            logger.info(f"Found {comment_count} issues that require attention.")

    except Exception as e:
        logger.critical(f"Fatal error in PR analysis: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        required_vars = [
            "GITHUB_REPOSITORY_ID",
            "GITHUB_TOKEN",
            "GITHUB_REPOSITORY",
            "CODE_REVIEW_API_ENDPOINT",
            "CODE_REVIEW_API_KEY",
        ]
        if missing_vars := [v for v in required_vars if not os.getenv(v)]:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        if not PR_NUMBER:
            raise ValueError("Could not determine PR number from environment variables")

        logger.info(f"Starting GitHub PR analysis for PR #{PR_NUMBER}")
        github_pr_ai_analyzer(PR_NUMBER)

    except Exception as e:
        logger.critical(f"Failed to run GitHub PR analyzer: {e}", exc_info=True)
        raise
