from django.contrib import admin

from apps.city.models import (
    AIRequest,
    ChatConversation,
    ChatMessage,
    FeedComment,
    FeedPost,
    FeedPostMedia,
    FeedReaction,
    Follow,
    Review,
    Story,
    StorySlide,
)


class FeedPostMediaInline(admin.TabularInline):
    model = FeedPostMedia
    extra = 0
    fields = ('media', 'sort_order')
    autocomplete_fields = ('media',)


class FeedCommentInline(admin.TabularInline):
    model = FeedComment
    extra = 0
    fields = ('user', 'parent', 'body', 'status', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('user', 'parent')


class StorySlideInline(admin.TabularInline):
    model = StorySlide
    extra = 0
    fields = ('media', 'caption', 'cta_label', 'cta_url', 'sort_order')
    autocomplete_fields = ('media',)


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    fields = ('sender', 'body', 'media', 'read_at', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('sender', 'media')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'user', 'order', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('business__name', 'user__email', 'text')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('business', 'user', 'order')
    list_editable = ('status',)
    date_hierarchy = 'created_at'


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'city', 'business', 'author_user', 'type', 'status', 'published_at', 'created_at')
    list_filter = ('type', 'status', 'city', 'published_at', 'created_at')
    search_fields = ('title', 'body', 'tags', 'business__name', 'author_user__email')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('city', 'business', 'author_user')
    inlines = (FeedPostMediaInline, FeedCommentInline)
    list_editable = ('status',)
    date_hierarchy = 'published_at'


@admin.register(FeedPostMedia)
class FeedPostMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'media', 'sort_order')
    search_fields = ('post__title', 'media__object_key')
    readonly_fields = ('id',)
    autocomplete_fields = ('post', 'media')


@admin.register(FeedComment)
class FeedCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'parent', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('post__title', 'user__email', 'body')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('post', 'user', 'parent')
    list_editable = ('status',)


@admin.register(FeedReaction)
class FeedReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'reaction', 'created_at')
    list_filter = ('reaction', 'created_at')
    search_fields = ('post__title', 'user__email')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('post', 'user')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'business', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'business__name')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('user', 'business')


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'city', 'business', 'status', 'expires_at', 'created_at')
    list_filter = ('status', 'city', 'expires_at', 'created_at')
    search_fields = ('title', 'business__name')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('city', 'business')
    inlines = (StorySlideInline,)
    list_editable = ('status',)


@admin.register(StorySlide)
class StorySlideAdmin(admin.ModelAdmin):
    list_display = ('id', 'story', 'media', 'cta_label', 'sort_order')
    search_fields = ('story__title', 'caption', 'cta_label')
    readonly_fields = ('id',)
    autocomplete_fields = ('story', 'media')


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'city', 'kind', 'business', 'order', 'listing', 'buyer', 'seller', 'last_message_at', 'created_at'
    )
    list_filter = ('kind', 'city', 'last_message_at', 'created_at')
    search_fields = ('business__name', 'buyer__email', 'seller__email')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('city', 'business', 'order', 'listing', 'buyer', 'seller')
    inlines = (ChatMessageInline,)
    date_hierarchy = 'created_at'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'short_body', 'read_at', 'created_at')
    list_filter = ('read_at', 'created_at')
    search_fields = ('sender__email', 'body')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('conversation', 'sender', 'media')

    @admin.display(description='Сообщение')
    def short_body(self, obj):
        return (obj.body or '')[:80]


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'city', 'short_prompt', 'created_at')
    list_filter = ('city', 'created_at')
    search_fields = ('user__email', 'prompt')
    readonly_fields = ('id', 'response', 'created_at')
    autocomplete_fields = ('user', 'city')

    @admin.display(description='Запрос')
    def short_prompt(self, obj):
        return obj.prompt[:80]
