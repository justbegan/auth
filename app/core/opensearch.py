import logging
from functools import lru_cache
from typing import Any

from django.conf import settings
from opensearchpy import OpenSearch

logger = logging.getLogger(__name__)


def _to_float(value: Any) -> float | None:
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_hit_id(hit: dict[str, Any]) -> str | None:
    source = hit.get('_source') or {}
    source_id = source.get('id')
    if source_id:
        return str(source_id)
    hit_id = hit.get('_id')
    if hit_id:
        return str(hit_id)
    return None


def _safe_search(index: str, body: dict[str, Any]) -> list[str] | None:
    client = get_client()
    if client is None:
        return None
    try:
        response = client.search(index=index, body=body)
    except Exception as exc:  # pragma: no cover - network/runtime dependent
        logger.warning('OpenSearch search failed for index=%s: %s', index, exc)
        return None

    hits = response.get('hits', {}).get('hits', [])
    ids = []
    for hit in hits:
        item_id = _extract_hit_id(hit)
        if item_id:
            ids.append(item_id)
    return ids


@lru_cache(maxsize=1)
def get_client() -> OpenSearch | None:
    url = getattr(settings, 'OPENSEARCH_URL', '')
    if not url:
        return None
    try:
        return OpenSearch(hosts=[url], timeout=2)
    except Exception as exc:  # pragma: no cover - runtime dependent
        logger.warning('OpenSearch client init failed: %s', exc)
        return None


def search_business_ids(
    *,
    city_id,
    q: str | None = None,
    category_id: str | None = None,
    rating_min: float | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    size: int = 200,
) -> list[str] | None:
    filters: list[dict[str, Any]] = [
        {'term': {'city_id': str(city_id)}},
        {'term': {'status': 'active'}},
    ]
    if category_id:
        filters.append({'term': {'category_id': str(category_id)}})
    rating_min_value = _to_float(rating_min)
    price_min_value = _to_float(price_min)
    price_max_value = _to_float(price_max)

    if rating_min_value is not None:
        filters.append({'range': {'rating': {'gte': rating_min_value}}})
    if price_min_value is not None or price_max_value is not None:
        range_part: dict[str, float] = {}
        if price_min_value is not None:
            range_part['gte'] = price_min_value
        if price_max_value is not None:
            range_part['lte'] = price_max_value
        filters.append({'range': {'min_product_price': range_part}})

    body: dict[str, Any] = {
        'size': size,
        'query': {'bool': {'filter': filters}},
    }
    if q:
        body['query']['bool']['must'] = [
            {
                'multi_match': {
                    'query': q,
                    'fields': ['name^4', 'description^2', 'products.name', 'products.description'],
                    'fuzziness': 'AUTO',
                }
            }
        ]
    else:
        body['sort'] = [{'rating': {'order': 'desc'}}]

    return _safe_search(settings.OPENSEARCH_INDEX_BUSINESSES, body)


def search_board_listing_ids(
    *,
    city_id,
    q: str | None = None,
    category_slug: str | None = None,
    category_id: str | None = None,
    subcategory_id: str | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    condition: str | None = None,
    seller_type: str | None = None,
    district: str | None = None,
    negotiable: bool | None = None,
    size: int = 300,
) -> list[str] | None:
    filters: list[dict[str, Any]] = [
        {'term': {'city_id': str(city_id)}},
        {'term': {'status': 'active'}},
    ]

    if category_slug:
        filters.append({'term': {'category_slug': category_slug}})
    if category_id:
        filters.append({'term': {'category_id': str(category_id)}})
    if subcategory_id:
        filters.append({'term': {'subcategory_id': str(subcategory_id)}})
    if condition:
        filters.append({'term': {'condition': condition}})
    if seller_type:
        filters.append({'term': {'seller_type': seller_type}})
    if district:
        filters.append({'term': {'district': district}})
    if negotiable is not None:
        filters.append({'term': {'negotiable': bool(negotiable)}})
    price_min_value = _to_float(price_min)
    price_max_value = _to_float(price_max)

    if price_min_value is not None or price_max_value is not None:
        range_part: dict[str, float] = {}
        if price_min_value is not None:
            range_part['gte'] = price_min_value
        if price_max_value is not None:
            range_part['lte'] = price_max_value
        filters.append({'range': {'price': range_part}})

    body: dict[str, Any] = {
        'size': size,
        'query': {'bool': {'filter': filters}},
        'sort': [
            {'boosted_until': {'order': 'desc', 'missing': '_last'}},
            {'created_at': {'order': 'desc'}},
        ],
    }
    if q:
        body['query']['bool']['must'] = [
            {
                'multi_match': {
                    'query': q,
                    'fields': ['title^4', 'description^2', 'attributes.value_text'],
                    'fuzziness': 'AUTO',
                }
            }
        ]

    return _safe_search(settings.OPENSEARCH_INDEX_BOARD, body)
