from rest_framework import serializers
from .models import Field, Voting


class FieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = Field
        fields = ('id', 'users', 'name', 'vote', 'count_votes')


class FieldVotingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Field
        fields = ('id', 'users', 'count_votes')


class VotingSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=True, read_only=True, source='fields')

    class Meta:
        model = Voting
        fields = ('id', 'name', 'meeting', 'all_votes', 'field')

