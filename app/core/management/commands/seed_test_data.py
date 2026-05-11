import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.admin_panel.models import Category
from apps.board.models import (
    BoardFavorite,
    BoardListing,
    BoardListingMedia,
    BoardListingStatsDaily,
    BoardReport,
)
from apps.business.models import (
    Business,
    BusinessAnalyticsDaily,
    BusinessLocation,
    BusinessWorkingHours,
    Order,
    OrderItem,
    Product,
)
from apps.city.models import FeedComment, FeedPost, FeedReaction, Follow, Review
from apps.profile.models import City, MediaFile, Notification, UserProfile
from apps.user.models import CustomUser


class Command(BaseCommand):
    help = "Наполняет базу тестовыми данными для локальной разработки"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=30, help="Количество обычных пользователей")
        parser.add_argument("--businesses", type=int, default=10, help="Количество бизнесов")
        parser.add_argument("--listings", type=int, default=20, help="Количество объявлений")
        parser.add_argument("--seed", type=int, default=42, help="Seed для random")
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить тестовые данные (с префиксом test_) перед заполнением",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])

        if options["clear"]:
            self._clear_test_data()

        cities = self._ensure_cities()
        categories = self._ensure_categories()
        users = self._create_users(options["users"], cities)
        businesses = self._create_businesses(options["businesses"], users, cities, categories["business"])
        products = self._create_products(businesses, categories["business"])
        self._create_orders_and_reviews(businesses, users, products)
        listings = self._create_board_listings(options["listings"], users, cities, categories["board"])
        self._create_city_feed(users, businesses, cities)
        self._create_notifications(users)
        self._create_board_activity(users, listings)

        self.stdout.write(
            self.style.SUCCESS(
                "Тестовые данные успешно созданы: "
                f"users={len(users)}, businesses={len(businesses)}, listings={len(listings)}"
            )
        )

    def _clear_test_data(self):
        BoardReport.objects.filter(reason__startswith="test_").delete()
        BoardFavorite.objects.filter(user__email__startswith="test_").delete()
        BoardListingStatsDaily.objects.filter(listing__title__startswith="test_").delete()
        BoardListingMedia.objects.filter(listing__title__startswith="test_").delete()
        BoardListing.objects.filter(title__startswith="test_").delete()

        FeedReaction.objects.filter(user__email__startswith="test_").delete()
        FeedComment.objects.filter(user__email__startswith="test_").delete()
        FeedPost.objects.filter(title__startswith="test_").delete()
        Follow.objects.filter(user__email__startswith="test_").delete()
        Review.objects.filter(text__startswith="test_").delete()

        OrderItem.objects.filter(order__customer__email__startswith="test_").delete()
        Order.objects.filter(customer__email__startswith="test_").delete()

        BusinessAnalyticsDaily.objects.filter(business__name__startswith="test_").delete()
        Product.objects.filter(name__startswith="test_").delete()
        BusinessWorkingHours.objects.filter(business__name__startswith="test_").delete()
        BusinessLocation.objects.filter(business__name__startswith="test_").delete()
        Business.objects.filter(name__startswith="test_").delete()

        Notification.objects.filter(user__email__startswith="test_").delete()
        UserProfile.objects.filter(user__email__startswith="test_").delete()
        MediaFile.objects.filter(owner__email__startswith="test_").delete()
        CustomUser.objects.filter(email__startswith="test_").delete()

    def _ensure_cities(self):
        city_specs = [
            ("yakutsk", "Якутск", "Республика Саха (Якутия)", 129.7326, 62.0272),
            ("moscow", "Москва", "Москва", 37.6173, 55.7558),
            ("spb", "Санкт-Петербург", "Ленинградская область", 30.3351, 59.9343),
        ]
        cities = []
        for slug, name, region, lng, lat in city_specs:
            city, _ = City.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "region": region,
                    "timezone": "Asia/Yakutsk" if slug == "yakutsk" else "Europe/Moscow",
                    "point": Point(lng, lat, srid=4326),
                    "is_active": True,
                },
            )
            cities.append(city)
        return cities

    def _ensure_categories(self):
        category_map = {"business": [], "board": [], "city": []}
        for section in (Category.Section.BUSINESS, Category.Section.BOARD, Category.Section.CITY):
            for i in range(1, 4):
                category, _ = Category.objects.get_or_create(
                    section=section,
                    slug=f"test_{section}_{i}",
                    defaults={
                        "name": f"test_{section}_{i}",
                        "sort_order": i,
                        "is_active": True,
                    },
                )
                category_map[section].append(category)
        return category_map

    def _create_users(self, users_count, cities):
        users = []

        def make_user(email, account_type, idx):
            username = email.split("@")[0]
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "phone": f"+7999000{idx:04d}",
                    "account_type": account_type,
                    "status": CustomUser.Status.ACTIVE,
                },
            )
            if created:
                user.set_password("12345678")
                user.save(update_fields=["password"])
            return user

        admin_user = make_user("test_admin@example.com", CustomUser.AccountType.ADMIN, 1)
        users.append(admin_user)

        for i in range(2, users_count + 2):
            account_type = CustomUser.AccountType.USER
            if i % 4 == 0:
                account_type = CustomUser.AccountType.BUSINESS
            user = make_user(f"test_user_{i}@example.com", account_type, i)
            users.append(user)

        for idx, user in enumerate(users, start=1):
            avatar, _ = MediaFile.objects.get_or_create(
                owner=user,
                object_key=f"test_avatars/{user.id}.jpg",
                defaults={
                    "bucket": "test-bucket",
                    "url": f"https://cdn.example.com/test_avatars/{user.id}.jpg",
                    "mime_type": "image/jpeg",
                    "size_bytes": 42_000,
                    "width": 512,
                    "height": 512,
                },
            )
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "first_name": f"Имя{idx}",
                    "last_name": f"Фамилия{idx}",
                    "avatar_media": avatar,
                    "city": random.choice(cities),
                    "metadata": {"is_test": True},
                },
            )
        return users

    def _create_businesses(self, businesses_count, users, cities, categories):
        owners = [u for u in users if u.account_type in (CustomUser.AccountType.BUSINESS, CustomUser.AccountType.ADMIN)]
        businesses = []
        for i in range(1, businesses_count + 1):
            owner = random.choice(owners)
            city = random.choice(cities)
            category = random.choice(categories)
            business, _ = Business.objects.get_or_create(
                city=city,
                slug=f"test_business_{i}",
                defaults={
                    "owner": owner,
                    "category": category,
                    "name": f"test_business_{i}",
                    "description": f"test_description_business_{i}",
                    "status": random.choice(
                        [Business.Status.ACTIVE, Business.Status.PENDING, Business.Status.DRAFT]
                    ),
                    "phone": f"+7999555{i:04d}",
                    "email": f"test_business_{i}@example.com",
                    "website": f"https://test-business-{i}.example.com",
                    "rating": Decimal(str(round(random.uniform(3.6, 5.0), 1))),
                    "reviews_count": random.randint(0, 120),
                },
            )
            businesses.append(business)

            BusinessLocation.objects.get_or_create(
                business=business,
                address=f"test_address_{i}",
                defaults={
                    "district": f"test_district_{random.randint(1, 5)}",
                    "point": Point(
                        city.point.x + random.uniform(-0.05, 0.05),
                        city.point.y + random.uniform(-0.05, 0.05),
                        srid=4326,
                    ),
                    "geohash": f"test_gh_{i}",
                    "is_main": True,
                },
            )

            for day in range(7):
                BusinessWorkingHours.objects.get_or_create(
                    business=business,
                    day_of_week=day,
                    defaults={
                        "open_time": None if day == 6 else "09:00",
                        "close_time": None if day == 6 else "21:00",
                        "is_closed": day == 6,
                    },
                )
            BusinessAnalyticsDaily.objects.get_or_create(
                business=business,
                day=timezone.now().date(),
                defaults={
                    "views": random.randint(100, 1000),
                    "orders_count": random.randint(5, 60),
                    "revenue_total": Decimal(random.randint(10_000, 500_000)),
                    "conversion_rate": Decimal(str(round(random.uniform(1.0, 9.0), 2))),
                    "avg_check": Decimal(random.randint(600, 5000)),
                },
            )
        return businesses

    def _create_products(self, businesses, categories):
        products = []
        for business in businesses:
            for j in range(1, 6):
                product, _ = Product.objects.get_or_create(
                    business=business,
                    name=f"test_product_{business.slug}_{j}",
                    defaults={
                        "category": random.choice(categories),
                        "description": f"test_product_description_{j}",
                        "sku": f"TEST-{business.slug.upper()}-{j}",
                        "price": Decimal(random.randint(100, 5000)),
                        "old_price": Decimal(random.randint(200, 7000)),
                        "stock_qty": random.randint(0, 200),
                        "is_active": True,
                        "sort_order": j,
                    },
                )
                products.append(product)
        return products

    def _create_orders_and_reviews(self, businesses, users, products):
        customers = [u for u in users if u.account_type == CustomUser.AccountType.USER]
        products_by_business = {}
        for p in products:
            products_by_business.setdefault(p.business_id, []).append(p)

        for business in businesses:
            biz_products = products_by_business.get(business.id, [])
            if not biz_products:
                continue

            for _ in range(3):
                customer = random.choice(customers)
                product = random.choice(biz_products)
                qty = Decimal(random.choice(["1", "2", "3"]))
                subtotal = product.price * qty
                delivery_fee = Decimal(random.choice([0, 99, 149]))
                total = subtotal + delivery_fee
                order = Order.objects.create(
                    city=business.city,
                    business=business,
                    customer=customer,
                    status=random.choice(
                        [Order.Status.CREATED, Order.Status.CONFIRMED, Order.Status.COMPLETED]
                    ),
                    delivery_type=random.choice([Order.DeliveryType.DELIVERY, Order.DeliveryType.PICKUP]),
                    payment_status=random.choice([Order.PaymentStatus.PENDING, Order.PaymentStatus.PAID]),
                    subtotal=subtotal,
                    delivery_fee=delivery_fee,
                    discount_total=Decimal("0"),
                    total=total,
                    currency="RUB",
                    address={"street": "test_street", "house": "1"},
                    scheduled_at=timezone.now() + timedelta(hours=random.randint(1, 48)),
                )
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    name_snapshot=product.name,
                    qty=qty,
                    price=product.price,
                    total=subtotal,
                )
                Review.objects.create(
                    business=business,
                    user=customer,
                    order=order,
                    rating=random.randint(3, 5),
                    text=f"test_review_for_{business.slug}",
                    status=Review.Status.PUBLISHED,
                )

    def _create_board_listings(self, listings_count, users, cities, categories):
        sellers = [u for u in users if u.account_type in (CustomUser.AccountType.USER, CustomUser.AccountType.BUSINESS)]
        listings = []
        for i in range(1, listings_count + 1):
            city = random.choice(cities)
            listing = BoardListing.objects.create(
                city=city,
                seller=random.choice(sellers),
                category=random.choice(categories),
                subcategory=random.choice(categories),
                title=f"test_listing_{i}",
                description=f"test_description_listing_{i}",
                price=Decimal(random.randint(500, 50_000)),
                condition=random.choice([BoardListing.Condition.NEW, BoardListing.Condition.USED]),
                seller_type=random.choice([BoardListing.SellerType.PRIVATE, BoardListing.SellerType.BUSINESS]),
                status=random.choice([BoardListing.Status.ACTIVE, BoardListing.Status.REVIEW]),
                negotiable=bool(i % 2),
                district=f"test_district_{random.randint(1, 7)}",
                address=f"test_listing_address_{i}",
                point=Point(
                    city.point.x + random.uniform(-0.1, 0.1),
                    city.point.y + random.uniform(-0.1, 0.1),
                    srid=4326,
                ),
                views_count=random.randint(0, 1000),
                contacts_count=random.randint(0, 100),
                favorites_count=random.randint(0, 100),
                expires_at=timezone.now() + timedelta(days=30),
            )
            listings.append(listing)

            media = MediaFile.objects.create(
                owner=listing.seller,
                bucket="test-bucket",
                object_key=f"test_board_media/{listing.id}.jpg",
                url=f"https://cdn.example.com/test_board_media/{listing.id}.jpg",
                mime_type="image/jpeg",
                size_bytes=100_000,
                width=1280,
                height=720,
            )
            BoardListingMedia.objects.create(listing=listing, media=media, sort_order=0)
            BoardListingStatsDaily.objects.get_or_create(
                listing=listing,
                day=timezone.now().date(),
                defaults={
                    "views": random.randint(1, 300),
                    "contacts": random.randint(0, 40),
                    "favorites": random.randint(0, 25),
                },
            )
        return listings

    def _create_city_feed(self, users, businesses, cities):
        author_users = [u for u in users if u.account_type in (CustomUser.AccountType.ADMIN, CustomUser.AccountType.BUSINESS)]
        for i in range(1, 8):
            post = FeedPost.objects.create(
                city=random.choice(cities),
                business=random.choice(businesses),
                author_user=random.choice(author_users),
                type=random.choice([FeedPost.Type.POST, FeedPost.Type.NEWS, FeedPost.Type.PROMO]),
                title=f"test_post_{i}",
                body=f"test_body_post_{i}",
                tags=["test", "seed"],
                status=FeedPost.Status.PUBLISHED,
                published_at=timezone.now() - timedelta(days=random.randint(0, 7)),
            )
            for _ in range(2):
                user = random.choice(users)
                FeedComment.objects.create(post=post, user=user, body=f"test_comment_for_{post.id}")
                FeedReaction.objects.get_or_create(post=post, user=user, reaction="like")

        for business in random.sample(businesses, min(5, len(businesses))):
            Follow.objects.get_or_create(user=random.choice(users), business=business)

    def _create_notifications(self, users):
        for user in random.sample(users, min(15, len(users))):
            Notification.objects.create(
                user=user,
                type="test_notification",
                title="test_notification_title",
                body="test_notification_body",
                entity_type="seed",
            )

    def _create_board_activity(self, users, listings):
        for listing in random.sample(listings, min(10, len(listings))):
            user = random.choice(users)
            BoardFavorite.objects.get_or_create(user=user, listing=listing)
            BoardReport.objects.get_or_create(
                listing=listing,
                reporter=user,
                reason="test_spam",
                defaults={"comment": "test_report_comment"},
            )
