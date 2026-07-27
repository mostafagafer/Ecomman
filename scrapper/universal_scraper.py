import json
import re
import time
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any
from urllib.parse import urlparse

import ollama
import httpx
from ddgs import DDGS
from ddgs.exceptions import DDGSException
from scrapling.fetchers import Fetcher, StealthyFetcher


OLLAMA_HOST = "http://127.0.0.1:11434"

NOT_FOUND_SIGNALS = (
    "page not found",
    "404",
    "not found",
    "has moved",
    "no longer available",
    "does not exist",
    "لم يتم العثور",
)

PRODUCT_SIGNALS = (
    "price",
    "sar",
    "add to cart",
    "buy now",
    "out of stock",
    "in stock",
    "availability",
    "sku",
    "product description",
    "description",
    "brand",
    "reviews",
    "rating",
    "cart",
    "ريال",
    "أضف",
    "السلة",
)

LISTING_PAGE_SIGNALS = (
    "sort by",
    "filter",
    "filters",
    "view as grid",
    "grid list",
    "per page",
    "show all",
    "category",
    "categories",
    "recommended",
    "apply",
)


@dataclass
class ChannelInput:
    name: str
    website_url: str


def normalize_site_scope(website_url: str) -> str:
    parsed = urlparse(website_url)
    domain = parsed.netloc or parsed.path
    path = parsed.path.strip("/") if parsed.netloc else ""
    return f"{domain}/{path}" if path else domain


def normalize_url_for_scope(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    return f"{parsed.netloc}/{path}" if path else parsed.netloc


def build_site_search_query(website_url: str, product_name: str) -> str:
    site_scope = normalize_site_scope(website_url)
    return f'site:{site_scope} "{product_name}"'


def build_site_search_queries(website_url: str, product_name: str) -> list[str]:
    site_scope = normalize_site_scope(website_url)
    return [
        f'site:{site_scope} "{product_name}"',
        f"site:{site_scope} {product_name}",
    ]


def fetch_html(url: str, timeout: int = 30, stealth: bool = False) -> str:
    page = (
        StealthyFetcher.fetch(url, timeout=timeout * 1000, headless=True)
        if stealth
        else Fetcher.get(url, timeout=timeout)
    )
    html = getattr(page, "html", None) or getattr(page, "body", None) or str(page)
    return html.decode("utf-8", errors="ignore") if isinstance(html, bytes) else html


def simplify_html(html: str, max_chars: int | None = 12000) -> str:
    html = re.sub(r"(?is)<script.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?</style>", " ", html)
    html = re.sub(r"(?is)<svg.*?</svg>", " ", html)
    html = re.sub(r"(?is)<(nav|header|footer).*?</\1>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", "\n", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    html = re.sub(r"[ \t]{2,}", " ", html)
    text = html.strip()
    return text[:max_chars] if max_chars else text


def get_page_text(html: str, max_chars: int = 20000) -> str:
    return simplify_html(html, max_chars=max_chars).lower()


def _extract_tag_values(html: str, pattern: str, limit: int = 10) -> list[str]:
    values = []
    for match in re.findall(pattern, html, flags=re.IGNORECASE | re.DOTALL):
        value = re.sub(r"\s+", " ", match).strip()
        if value and value not in values:
            values.append(value)
        if len(values) >= limit:
            break
    return values


def _truncate(value: str | None, max_chars: int) -> str | None:
    if value is None:
        return None
    return value[:max_chars]


def build_product_evidence(html: str, max_chars: int = 2500) -> dict[str, Any]:
    text = simplify_html(html, max_chars=None)
    raw_price_lines = [
        line.strip()
        for line in text.splitlines()
        if re.search(r"\b(price|sar|discount|save|ريال|ر\.س)\b", line, re.IGNORECASE)
    ][:10]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    price_line_indexes = [
        index
        for index, line in enumerate(lines)
        if line in raw_price_lines
        or re.search(r"\b(price|sar|discount|save|was|now|off|vat)\b", line, re.IGNORECASE)
    ]
    price_context_indexes = set()
    for index in price_line_indexes:
        for nearby_index in range(max(0, index - 3), min(len(lines), index + 4)):
            price_context_indexes.add(nearby_index)
    price_lines = [lines[index] for index in sorted(price_context_indexes)][:30]

    meta = _extract_tag_values(
        html,
        r'<meta[^>]+(?:name|property)=["\'](?:description|og:title|og:description|og:image|product:price:amount|product:availability)["\'][^>]+content=["\']([^"\']+)["\']',
        limit=8,
    )
    json_ld = _extract_tag_values(
        html,
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        limit=2,
    )

    return {
        "page_title": (_extract_tag_values(html, r"<title[^>]*>(.*?)</title>", limit=1) or [None])[0],
        "meta": [_truncate(item, 500) for item in meta],
        "json_ld": [_truncate(item, 1500) for item in json_ld],
        "image_urls": re.findall(r'https?://[^"\']+\.(?:jpg|jpeg|png|webp)', html, flags=re.IGNORECASE)[:5],
        "price_related_lines": price_lines,
        "visible_text": text[:max_chars],
    }


def summarize_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "total_chars": len(json.dumps(evidence, ensure_ascii=False)),
        "meta_count": len(evidence.get("meta") or []),
        "meta_chars": sum(len(item or "") for item in evidence.get("meta") or []),
        "json_ld_count": len(evidence.get("json_ld") or []),
        "json_ld_chars": sum(len(item or "") for item in evidence.get("json_ld") or []),
        "image_count": len(evidence.get("image_urls") or []),
        "price_line_count": len(evidence.get("price_related_lines") or []),
        "visible_text_chars": len(evidence.get("visible_text") or ""),
    }


def evaluate_product_page(html: str) -> dict[str, Any]:
    text = get_page_text(html)
    not_found_hits = [signal for signal in NOT_FOUND_SIGNALS if signal in text]
    product_hits = [signal for signal in PRODUCT_SIGNALS if signal in text]
    listing_hits = [signal for signal in LISTING_PAGE_SIGNALS if signal in text]
    strong_product_hits = [
        signal
        for signal in product_hits
        if signal in ("sku", "product description", "description", "reviews", "rating")
    ]

    return {
        "is_live": not not_found_hits,
        "looks_like_product": len(product_hits) >= 2 and (
            len(strong_product_hits) >= 1 or len(listing_hits) < 2
        ),
        "not_found_signals": not_found_hits,
        "product_signals": product_hits,
        "listing_signals": listing_hits,
    }


def discover_product_candidates(
    website_url: str,
    product_name: str,
    limit: int = 5,
    timeout: int = 30,
    backend: str = "auto",
    attempts: int = 3,
) -> list[dict[str, str | None]]:
    site_scope = normalize_site_scope(website_url)
    candidates = []
    seen_urls = set()

    for query in build_site_search_queries(website_url, product_name):
        for _ in range(attempts):
            try:
                with DDGS(timeout=timeout) as ddgs:
                    results = ddgs.text(
                        query,
                        max_results=limit * 4,
                        backend=backend,
                    )
            except DDGSException:
                continue

            for result in results:
                url = result.get("href") or result.get("url")
                if not url:
                    continue

                clean_scope = normalize_url_for_scope(url)
                if clean_scope.startswith(site_scope) and url not in seen_urls:
                    seen_urls.add(url)
                    candidates.append(
                        {
                            "title": result.get("title"),
                            "url": url,
                            "body": result.get("body"),
                        }
                    )

                if len(candidates) >= limit:
                    return candidates

            if candidates:
                return candidates

    return candidates


def search_raw_results(
    website_url: str,
    product_name: str,
    limit: int = 20,
    timeout: int = 30,
    backend: str = "auto",
) -> list[dict[str, Any]]:
    with DDGS(timeout=timeout) as ddgs:
        return ddgs.text(
            build_site_search_query(website_url, product_name),
            max_results=limit,
            backend=backend,
        )


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.lower())


def _numbers(value: str) -> list[str]:
    return re.findall(r"\d+", value.lower())


def _similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left.lower(), right.lower()).ratio()


def score_candidate(product_name: str, candidate: dict[str, str | None]) -> dict[str, Any]:
    title = candidate.get("title") or ""
    body = candidate.get("body") or ""
    url = candidate.get("url") or ""
    text = f"{title} {body}".lower()
    title_text = title.lower()
    body_text = body.lower()
    url_text = url.lower()

    product_tokens = [token for token in _tokens(product_name) if len(token) > 1]
    product_numbers = _numbers(product_name)
    title_numbers = set(_numbers(title_text))
    body_numbers = set(_numbers(body_text))
    candidate_numbers = title_numbers | body_numbers
    score = 0
    reasons = []

    title_similarity = _similarity(product_name, title)
    title_similarity_score = int(title_similarity * 30)
    score += title_similarity_score
    reasons.append(f"title similarity: {title_similarity_score}")

    if product_tokens:
        best_first_token_similarity = max(
            _similarity(product_tokens[0], token)
            for token in _tokens(title)
        ) if _tokens(title) else 0
        first_token_score = int(best_first_token_similarity * 15)
        score += first_token_score
        reasons.append(f"first token similarity: {first_token_score}")

    for token in product_tokens:
        if token in title_text:
            score += 10
            reasons.append(f"title token: {token}")
        elif token in body_text:
            score += 1
            reasons.append(f"text token: {token}")

    for number in product_numbers:
        if number in title_numbers:
            score += 8
            reasons.append(f"title number match: {number}")
        elif number in body_numbers:
            score += 2
            reasons.append(f"body number match: {number}")

    for number in title_numbers:
        if number not in product_numbers:
            score -= 4
            reasons.append(f"extra title number: {number}")

    variant_terms = (
        "spf",
        "plus",
        "lotion",
        "ointment",
        "refill",
        "twin",
        "pack",
        "bundle",
        "2+1",
    )
    product_lower = product_name.lower()
    for term in variant_terms:
        if term in text and term not in product_lower:
            score -= 5
            reasons.append(f"variant penalty: {term}")

    listing_terms = ("sort by", "filter", "category", "best ", "/c/", "grid", "per page")
    for term in listing_terms:
        if term in title_text or term in body_text or term in url_text:
            score -= 12
            reasons.append(f"listing penalty: {term.strip()}")

    if product_tokens and not any(token in title_text for token in product_tokens):
        score -= 10
        reasons.append("no exact product token in title")

    return {
        "score": score,
        "reasons": reasons,
    }


def rank_candidates(
    product_name: str,
    candidates: list[dict[str, str | None]],
) -> list[dict[str, Any]]:
    ranked = []
    for candidate in candidates:
        scoring = score_candidate(product_name, candidate)
        ranked.append({**candidate, **scoring})

    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def pick_best_candidate(
    product_name: str,
    candidates: list[dict[str, str | None]],
) -> dict[str, Any] | None:
    ranked = rank_candidates(product_name, candidates)
    return ranked[0] if ranked else None


def fetch_valid_product_pages(
    candidates: list[dict[str, str | None]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    pages = []

    for candidate in candidates:
        url = candidate.get("url")
        if not url:
            continue

        for fetch_mode in ("normal", "stealth"):
            try:
                html = fetch_html(url, stealth=fetch_mode == "stealth")
            except Exception as exc:
                pages.append(
                    {
                        "url": url,
                        "valid": False,
                        "fetch_mode": fetch_mode,
                        "error": str(exc),
                        "candidate": candidate,
                    }
                )
                continue

            evaluation = evaluate_product_page(html)
            is_valid = evaluation["is_live"] and evaluation["looks_like_product"]
            pages.append(
                {
                    "url": url,
                    "valid": is_valid,
                    "fetch_mode": fetch_mode,
                    "evaluation": evaluation,
                    "candidate": candidate,
                    "title": candidate.get("title"),
                    "body": candidate.get("body"),
                    "html": html if is_valid else None,
                    "content": simplify_html(html) if is_valid else None,
                }
            )

            if is_valid:
                break

        if sum(1 for page in pages if page.get("valid")) >= limit:
            break

    return pages


def extract_product_with_ollama(
    model: str,
    channel: ChannelInput,
    product_name: str,
    pages: list[dict[str, str]],
    timeout: int = 600,
    num_ctx: int = 4096,
    num_predict: int = 600,
    progress=None,
) -> dict[str, Any]:
    page_payload = pages[0] if pages else {}
    prompt = (
        "You extract ecommerce product data from compact page evidence.\n"
        "Return only valid JSON. Do not include markdown. Do not explain outside JSON.\n"
        "Use only the supplied evidence. Do not guess. Use null when a field is not present.\n"
        "If a field is missing, add a short reason in extraction_issues.\n"
        "availability must be 1 for available, 0 for unavailable, or null when unclear.\n"
        "price and original_price must be numbers, not strings. confidence must be 0 to 1.\n"
        "Prefer exact product evidence over navigation, category, coupon, or unrelated image text.\n\n"
        f"Target product: {product_name}\n"
        f"Channel: {channel.name}\n"
        f"Website: {channel.website_url}\n\n"
        "JSON schema:\n"
        '{"matched_url": null, "name": null, "price": null, '
        '"original_price": null, "discount": null, "availability": null, '
        '"image_url": null, "description": null, "sku": null, '
        '"confidence": 0, "extraction_issues": []}\n\n'
        "Evidence:\n"
        f"{json.dumps(page_payload, ensure_ascii=False)}"
    )

    client = ollama.Client(host=OLLAMA_HOST, timeout=timeout)
    try:
        chunks = []
        started_at = time.monotonic()
        last_report_at = started_at
        chunk_count = 0
        for chunk in client.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0,
                "num_ctx": num_ctx,
                "num_predict": num_predict,
            },
            stream=True,
        ):
            content = chunk.get("message", {}).get("content") or ""
            if content:
                chunks.append(content)
                chunk_count += 1

            now = time.monotonic()
            if progress and now - last_report_at >= 5:
                progress(
                    "Ollama streaming: "
                    f"{chunk_count} chunk(s), "
                    f"{sum(len(item) for item in chunks)} character(s), "
                    f"{int(now - started_at)}s elapsed"
                )
                last_report_at = now
    except httpx.TimeoutException as exc:
        return {
            "matched_url": pages[0]["url"] if pages else None,
            "name": None,
            "price": None,
            "original_price": None,
            "discount": None,
            "availability": None,
            "image_url": None,
            "description": None,
            "sku": None,
            "confidence": 0,
            "extraction_issues": ["ollama_timeout"],
            "error": f"Ollama timed out after {timeout} seconds: {exc}",
        }

    raw_response = "".join(chunks).strip()
    if progress:
        progress(
            "Ollama stream completed: "
            f"{chunk_count} chunk(s), {len(raw_response)} character(s)"
        )

    try:
        return json.loads(raw_response)
    except json.JSONDecodeError as exc:
        return {
            "matched_url": pages[0]["url"] if pages else None,
            "name": None,
            "price": None,
            "original_price": None,
            "discount": None,
            "availability": None,
            "image_url": None,
            "description": None,
            "sku": None,
            "confidence": 0,
            "extraction_issues": ["ollama_returned_invalid_json"],
            "error": f"Ollama returned invalid JSON: {exc}",
            "raw_response": raw_response[:1000],
        }


def build_pipeline_debug(
    ranked_candidates: list[dict[str, Any]],
    fetched_pages: list[dict[str, Any]],
    pages: list[dict[str, Any]],
) -> dict[str, Any]:
    selected_candidate = None
    if pages:
        selected_url = pages[0].get("url")
        selected_candidate = next(
            (candidate for candidate in ranked_candidates if candidate.get("url") == selected_url),
            ranked_candidates[0] if ranked_candidates else None,
        )
    elif ranked_candidates:
        selected_candidate = ranked_candidates[0]
    return {
        "discovery": {
            "candidate_count": len(ranked_candidates),
            "ranked_candidates": ranked_candidates,
        },
        "selection": {
            "selected_candidate": selected_candidate,
        },
        "fetch_validation": {
            "fetched_count": len(fetched_pages),
            "validated_pages": [
                {
                    "url": page["url"],
                    "valid": page.get("valid"),
                    "fetch_mode": page.get("fetch_mode"),
                    "evaluation": page.get("evaluation"),
                    "error": page.get("error"),
                }
                for page in fetched_pages
            ],
        },
        "ollama_input": pages[0].get("evidence_summary") if pages else None,
    }


def scrape_product_with_ollama(
    channel: ChannelInput,
    product_name: str,
    model: str = "qwen3-coder:30b",
    candidate_limit: int = 3,
    backend: str = "auto",
    content_chars: int = 2500,
    ollama_timeout: int = 600,
    num_ctx: int = 4096,
    num_predict: int = 600,
    evidence_only: bool = False,
    progress=None,
) -> dict[str, Any]:
    def report(message: str):
        if progress:
            progress(message)

    report("Discovering candidates with DDGS")
    candidates = discover_product_candidates(
        channel.website_url,
        product_name,
        limit=candidate_limit,
        backend=backend,
    )
    report(f"DDGS returned {len(candidates)} candidate(s)")

    ranked_candidates = rank_candidates(product_name, candidates)
    if ranked_candidates:
        report("Ranking candidates")
        for index, candidate in enumerate(ranked_candidates, start=1):
            report(
                f"#{index} score={candidate['score']} "
                f"title={candidate.get('title')} "
                f"url={candidate.get('url')}"
            )
    if ranked_candidates:
        report(
            "Selected candidate: "
            f"{ranked_candidates[0].get('title')} | {ranked_candidates[0].get('url')}"
        )
    else:
        report("No candidate selected")

    report("Fetching ranked candidates with Scrapling")
    fetched_pages = fetch_valid_product_pages(ranked_candidates, limit=1)
    report(f"Fetched {len(fetched_pages)} page attempt(s)")

    pages = []
    for page in fetched_pages:
        report(
            "Validation: "
            f"valid={page.get('valid')} "
            f"mode={page.get('fetch_mode')} "
            f"signals={page.get('evaluation', {}).get('product_signals', [])}"
        )
        if page.get("valid"):
            evidence = build_product_evidence(page["html"] or "", max_chars=content_chars)
            evidence_summary = summarize_evidence(evidence)
            report(
                "Prepared Ollama evidence: "
                f"{evidence_summary['total_chars']} character(s), "
                f"visible_text={evidence_summary['visible_text_chars']}, "
                f"meta={evidence_summary['meta_count']}/{evidence_summary['meta_chars']} chars, "
                f"json_ld={evidence_summary['json_ld_count']}/{evidence_summary['json_ld_chars']} chars, "
                f"images={evidence_summary['image_count']}, "
                f"price_lines={evidence_summary['price_line_count']}"
            )
            pages.append(
                {
                    "url": page["url"],
                    "search_title": page["candidate"]["title"],
                    "search_body": page["candidate"]["body"],
                    "evidence": evidence,
                    "evidence_summary": evidence_summary,
                }
            )

    if evidence_only:
        return {
            "channel": channel.name,
            "requested_product_name": product_name,
            "pipeline": build_pipeline_debug(ranked_candidates, fetched_pages, pages),
            "selected_page": pages[0] if pages else None,
        }

    if not pages:
        report("No valid product evidence found; skipping Ollama extraction")
        return {
            "channel": channel.name,
            "requested_product_name": product_name,
            "pipeline": build_pipeline_debug(ranked_candidates, fetched_pages, pages),
            "product": {
                "matched_url": None,
                "name": None,
                "price": None,
                "original_price": None,
                "discount": None,
                "availability": None,
                "image_url": None,
                "description": None,
                "sku": None,
                "confidence": 0,
                "extraction_issues": ["no_valid_product_evidence"],
                "error": "No fetched candidate contained enough product evidence for Ollama.",
            },
        }

    report(
        "Starting Ollama extraction "
        f"model={model}, num_ctx={num_ctx}, num_predict={num_predict}, timeout={ollama_timeout}s"
    )
    result = extract_product_with_ollama(
        model,
        channel,
        product_name,
        pages,
        timeout=ollama_timeout,
        num_ctx=num_ctx,
        num_predict=num_predict,
        progress=progress,
    )
    report("Ollama extraction finished")
    return {
        "channel": channel.name,
        "requested_product_name": product_name,
        "pipeline": build_pipeline_debug(ranked_candidates, fetched_pages, pages),
        "product": result,
    }
