from django.conf import settings
from django.core.management.base import BaseCommand
from opensearchpy.helpers import bulk

from apps.board.models import BoardListing
from apps.business.models import Business
from core.opensearch import get_client


BUSINESS_MAPPING = {
    'settings': {'number_of_shards': 1, 'number_of_replicas': 0},
    'mappings': {
        'properties': {
            'id': {'type': 'keyword'},
            'city_id': {'type': 'keyword'},
            'category_id': {'type': 'keyword'},
            'status': {'type': 'keyword'},
            'name': {'type': 'text'},
            'description': {'type': 'text'},
            'rating': {'type': 'float'},
            'min_product_price': {'type': 'float'},
            'products': {
                'type': 'nested',
                'properties': {
                    'name': {'type': 'text'},
                    'description': {'type': 'text'},
                },
            },
        }
    },
}

BOARD_MAPPING = {
    'settings': {'number_of_shards': 1, 'number_of_replicas': 0},
    'mappings': {
        'properties': {
            'id': {'type': 'keyword'},
            'city_id': {'type': 'keyword'},
            'category_id': {'type': 'keyword'},
            'category_slug': {'type': 'keyword'},
            'subcategory_id': {'type': 'keyword'},
            'status': {'type': 'keyword'},
            'title': {'type': 'text'},
            'description': {'type': 'text'},
            'price': {'type': 'float'},
            'condition': {'type': 'keyword'},
            'seller_type': {'type': 'keyword'},
            'district': {'type': 'keyword'},
            'negotiable': {'type': 'boolean'},
            'boosted_until': {'type': 'date'},
            'created_at': {'type': 'date'},
            'attributes': {
                'type': 'nested',
                'properties': {
                    'key': {'type': 'keyword'},
                    'value_text': {'type': 'text'},
                },
            },
        }
    },
}


class Command(BaseCommand):
    help = 'Синхронизирует индексы OpenSearch (businesses, board_listings).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить и пересоздать индексы перед синхронизацией.',
        )

    def handle(self, *args, **options):
        client = get_client()
        if client is None:
            self.stderr.write(self.style.ERROR('OpenSearch client is not configured.'))
            return

        should_reset = options.get('reset', False)

        businesses_index = settings.OPENSEARCH_INDEX_BUSINESSES
        board_index = settings.OPENSEARCH_INDEX_BOARD

        self._ensure_index(client, businesses_index, BUSINESS_MAPPING, should_reset)
        self._ensure_index(client, board_index, BOARD_MAPPING, should_reset)

        business_actions = self._build_business_actions(businesses_index)
        board_actions = self._build_board_actions(board_index)

        if business_actions:
            bulk(client, business_actions, refresh='wait_for')
        if board_actions:
            bulk(client, board_actions, refresh='wait_for')

        self.stdout.write(
            self.style.SUCCESS(
                f'OpenSearch sync completed: businesses={len(business_actions)}, board={len(board_actions)}'
            )
        )

    def _ensure_index(self, client, index_name: str, mapping: dict, should_reset: bool):
        exists = client.indices.exists(index=index_name)
        if exists and should_reset:
            client.indices.delete(index=index_name)
            exists = False
        if not exists:
            client.indices.create(index=index_name, body=mapping)

    def _build_business_actions(self, index_name: str):
        actions = []
        queryset = Business.objects.select_related('city', 'category').prefetch_related('products').all()
        for business in queryset:
            products = list(business.products.filter(is_active=True).values('name', 'description', 'price'))
            min_product_price = None
            if products:
                prices = [float(item['price']) for item in products if item.get('price') is not None]
                if prices:
                    min_product_price = min(prices)

            actions.append(
                {
                    '_op_type': 'index',
                    '_index': index_name,
                    '_id': str(business.id),
                    '_source': {
                        'id': str(business.id),
                        'city_id': str(business.city_id),
                        'category_id': str(business.category_id) if business.category_id else None,
                        'status': business.status,
                        'name': business.name,
                        'description': business.description or '',
                        'rating': float(business.rating),
                        'min_product_price': min_product_price,
                        'products': [
                            {
                                'name': item.get('name') or '',
                                'description': item.get('description') or '',
                            }
                            for item in products
                        ],
                    },
                }
            )
        return actions

    def _build_board_actions(self, index_name: str):
        actions = []
        queryset = BoardListing.objects.select_related('city', 'category', 'subcategory').prefetch_related('attributes')
        for listing in queryset:
            actions.append(
                {
                    '_op_type': 'index',
                    '_index': index_name,
                    '_id': str(listing.id),
                    '_source': {
                        'id': str(listing.id),
                        'city_id': str(listing.city_id),
                        'category_id': str(listing.category_id),
                        'category_slug': listing.category.slug if listing.category_id else None,
                        'subcategory_id': str(listing.subcategory_id) if listing.subcategory_id else None,
                        'status': listing.status,
                        'title': listing.title,
                        'description': listing.description,
                        'price': float(listing.price) if listing.price is not None else None,
                        'condition': listing.condition,
                        'seller_type': listing.seller_type,
                        'district': listing.district,
                        'negotiable': listing.negotiable,
                        'boosted_until': listing.boosted_until.isoformat() if listing.boosted_until else None,
                        'created_at': listing.created_at.isoformat() if listing.created_at else None,
                        'attributes': [
                            {'key': attr.key, 'value_text': attr.value_text or ''}
                            for attr in listing.attributes.all()
                        ],
                    },
                }
            )
        return actions
