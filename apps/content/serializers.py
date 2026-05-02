from rest_framework import serializers

from .models import BlogCategory, BlogPost, Partner, Service, Testimonial


class BlogCategorySerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = BlogCategory
        fields = "__all__"


class BlogPostSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = (
            "id",
            "slug",
            "title",
            "excerpt",
            "content",
            "title_en",
            "title_nl",
            "excerpt_en",
            "excerpt_nl",
            "content_en",
            "content_nl",
            "author_name",
            "featured_image",
            "featured_image_url",
            "image_url",
            "category",
            "category_name",
            "is_published",
            "published_at",
            "created_at",
            "updated_at",
        )

    def get_category_name(self, obj):
        return obj.category.display_name if obj.category else ""

    def get_title(self, obj):
        return obj.title_i18n

    def get_excerpt(self, obj):
        return obj.excerpt_i18n

    def get_content(self, obj):
        return obj.content_i18n

    def get_image_url(self, obj):
        url = obj.image_url
        if not url:
            return ""
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url


class ServiceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            "id",
            "slug",
            "name",
            "short_description",
            "details",
            "name_en",
            "name_nl",
            "short_description_en",
            "short_description_nl",
            "details_en",
            "details_nl",
            "icon_name",
            "image",
            "image_url",
            "display_order",
            "is_active",
        )

    def get_name(self, obj):
        return obj.name_i18n

    def get_short_description(self, obj):
        return obj.short_description_i18n

    def get_details(self, obj):
        return obj.details_i18n

    def get_image_url(self, obj):
        url = obj.image_url
        if not url:
            return ""
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url


class TestimonialSerializer(serializers.ModelSerializer):
    author_role = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Testimonial
        fields = (
            "id",
            "author_name",
            "author_role",
            "author_role_en",
            "author_role_nl",
            "message",
            "message_en",
            "message_nl",
            "photo",
            "photo_url",
            "rating",
            "display_order",
            "is_active",
            "created_at",
        )
        extra_kwargs = {
            "author_name": {"required": False, "allow_blank": True},
            "author_role_en": {"required": False, "allow_blank": True},
            "author_role_nl": {"required": False, "allow_blank": True},
            "message_en": {"required": False, "allow_blank": True},
            "message_nl": {"required": False, "allow_blank": True},
            "photo": {"required": False, "allow_null": True},
            "is_active": {"required": False},
            "display_order": {"required": False},
        }

    def get_author_role(self, obj):
        return obj.author_role_i18n

    def get_message(self, obj):
        return obj.message_i18n

    def get_photo_url(self, obj):
        url = obj.photo_url
        if not url:
            return ""
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def validate(self, attrs):
        # At least one of message_en / message_nl must be provided
        if not (attrs.get("message_en") or attrs.get("message_nl")):
            raise serializers.ValidationError(
                {"message": "A review message is required."}
            )
        rating = attrs.get("rating", 5)
        if rating < 1 or rating > 5:
            raise serializers.ValidationError({"rating": "Rating must be 1–5."})
        return attrs


class PartnerSerializer(serializers.ModelSerializer):
    logo_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields = (
            "id",
            "name",
            "logo",
            "logo_url",
            "logo_image_url",
            "website",
            "display_order",
            "is_active",
        )

    def get_logo_image_url(self, obj):
        url = obj.logo_image_url
        if not url:
            return ""
        if url.startswith("http"):
            return url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url
