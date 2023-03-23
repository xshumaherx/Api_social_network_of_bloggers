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
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username',)
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
    following = serializers.SlugRelatedField(queryset=User.objects.all(),
                                             slug_field='username',)
    user = serializers.SlugRelatedField(read_only=True,
                                        slug_field='username',)
    class Meta:
        model = Follow
        fields = ('user','following',)

    def validate(self, data):
        if self.context['request'].user == data.get('following'):
            raise serializers.ValidationError(
                'На себя нельзя подписаться'
            )
        if Follow.objects.filter(user=self.context['request'].user, 
                                 following=data['following']).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.'
            )
        return data
