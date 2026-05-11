from core.base.crud import CoreCrud
from apps.board.api.v1.serializers import BoardListingSerializer
from apps.board.models import BoardListing


class BoardListingServices(CoreCrud):
    model = BoardListing
    serializer = BoardListingSerializer
