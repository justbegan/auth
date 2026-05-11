from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.board.api.v1 import views

router = SimpleRouter()
router.register('my', views.MyBoardListingViewSet, basename='board-my')
router.register('favorites', views.BoardFavoriteViewSet, basename='board-favorites')
router.register('chat', views.BoardChatViewSet, basename='board-chat')

my_create = views.MyBoardListingViewSet.as_view({'post': 'create'})
my_update = views.MyBoardListingViewSet.as_view({'patch': 'partial_update'})

urlpatterns = [
    path('', views.BoardHomeView.as_view(), name='board-home'),
    path('categories', views.BoardCategoryListView.as_view(), name='board-categories'),
    path('c', views.BoardCatalogView.as_view(), name='board-catalog'),
    path('c/<slug:category>', views.BoardCatalogView.as_view(), name='board-category-catalog'),
    path('item/<uuid:listing_id>', views.BoardItemView.as_view(), name='board-item'),
    path('item/<uuid:listing_id>/favorite', views.BoardItemFavoriteView.as_view(), name='board-item-favorite'),
    path('item/<uuid:listing_id>/contact', views.BoardItemContactView.as_view(), name='board-item-contact'),
    path('item/<uuid:listing_id>/report', views.BoardItemReportView.as_view(), name='board-item-report'),
    path('favorites/<uuid:listing_id>', views.BoardFavoriteAddView.as_view(), name='board-favorite-add'),
    path('new', views.BoardNewReferencesView.as_view(), name='board-new-references'),
    path('new/create', my_create, name='board-new-create'),
    path('new/<uuid:pk>', my_update, name='board-new-update'),
    path('', include(router.urls)),
]
