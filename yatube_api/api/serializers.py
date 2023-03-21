import base64

from django.core.files.base import ContentFile
from posts.models import Comment, Group, Post, User, Follow
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка 
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')  
            # И извлечь расширение файла.
            ext = format.split('/')[-1]  
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username',)
    #group = serializers.SlugRelatedField(slug_field='slug',
    #                                     read_only=True,)
    image = Base64ImageField(required=False, allow_null=True)
    class Meta:
        model = Post
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username',)
    post = serializers.PrimaryKeyRelatedField(read_only=True,)

    class Meta:
        model = Comment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    posts = serializers.StringRelatedField(many=True,
                                           read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        ref_name = 'ReadOnlyUsers'


class FollowSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username',)
    user = User
    class Meta:
        model = Follow
        fields = ('user','following',)