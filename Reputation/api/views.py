from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import CommunityReputaionSerializer, ArticleScoreLogSerializer, ArticleUserScoreLogsSerializer, FlagReasonSerializer
from .serializers import MediaScoreLogSerializer, MediaUserScoreLogsSerializer
from Reputation.models import CommunityReputaion, ArticleScoreLog, ResourceScore, ArticleUserScoreLogs, ArticleFlagLogs, FlagReason
from Reputation.models import MediaScoreLog, MediaUserScoreLogs, MediaFlagLogs
from Media.models import Media
from BasicArticle.models import Articles
from rest_framework.permissions import IsAuthenticated
from Community.models import Community, CommunityMembership, CommunityArticles, CommunityGroups
from Group.models import GroupArticles
from django.http import Http404
from django.db.models import F
import json

class FetchCommunityReputation(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = CommunityReputaionSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        cid = self.kwargs['pk']
        community = Community.objects.get(id=cid)
        if CommunityMembership.objects.filter(community=community, user=self.request.user).exists():
            if CommunityReputaion.objects.filter(community=community, user=self.request.user).exists():
                return CommunityReputaion.objects.get(community=community, user=self.request.user)
            else:
                return CommunityReputaion.objects.create(community=community, user=self.request.user)


@api_view(['POST'])
def ArticlePublishScore(request):
    articleid = request.data['pk']
    article = ArticleScoreLog.objects.get(article=articleid)

    if not article.publish and article.article.state.name == 'publish':
        res = ResourceScore.objects.get(resource_type='resource')
        if CommunityArticles.objects.filter(article=article.article).exists():
            comm_article = CommunityArticles.objects.get(
                article=article.article)
            repu = CommunityReputaion.objects.get(
                community=comm_article.community, user=article.article.created_by)
            repu.score += res.publish_value
            repu.save()
            repu = CommunityReputaionSerializer(repu, many=False)
            return Response(repu.data)
        else:
            group_article = GroupArticles.objects.get(artcile=article.article)
            comm_group = CommunityGroups.objects.get(group=group_article.group)
            repu = CommunityReputaion.objects.get(
                community=comm_group.community, user=article.article.created_by)
            repu.score += res.publish_value
            repu.save()
            repu = CommunityReputaionSerializer(repu, many=False)
            return Response(repu.data)


class ReputationStats(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = ArticleScoreLog.objects.all()
    serializer_class = ArticleScoreLogSerializer


class ReputationStatsDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get_models_and_serializers(self, request):
        resource_type = self.request.query_params.get('resource_type')

        if (resource_type == 'article'):
            return ArticleScoreLog, ArticleUserScoreLogs, ArticleScoreLogSerializer, ArticleUserScoreLogsSerializer, ArticleFlagLogs, Articles
        elif (resource_type == 'media'):
            return MediaScoreLog, MediaUserScoreLogs, MediaScoreLogSerializer, MediaUserScoreLogsSerializer, MediaFlagLogs, Media
        else:
            raise Http404

    def get_object(self, pk):
        scoreLogModel, userLogModel, scoreLogSerializer, userLogSerializer, flagModel, model = self.get_models_and_serializers(self.request)

        try:
            try:
                resource = model.objects.get(pk=pk)
            except model.DoesNotExist:
                raise Http404
                
            resource_score_log, created = scoreLogModel.objects.get_or_create(resource=resource)
            return resource_score_log
        except scoreLogModel.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        scoreLogModel, userLogModel, scoreLogSerializer, userLogSerializer, flagModel, model = self.get_models_and_serializers(self.request)

        resource_score_log = self.get_object(pk)
        resource_user_log, created = userLogModel.objects.get_or_create(
            user=request.user,
            resource=resource_score_log.resource
        )

        resource_log_serializer = scoreLogSerializer(resource_score_log)
        user_log_serializer = userLogSerializer(resource_user_log)
        return Response({
            'resource_log': resource_log_serializer.data,
            'user_log': user_log_serializer.data
        })

    def post(self, request, pk):
        scoreLogModel, userLogModel, scoreLogSerializer, userLogSerializer, flagModel, model = self.get_models_and_serializers(self.request)

        resource_score_log = self.get_object(pk)

        updates = {
            'upvote': request.data.get('update_type') == 'upvote',
            'downvote': request.data.get('update_type') == 'downvote',
            'reported': request.data.get('update_type') == 'reported'
        }

        resource_user_log, created = userLogModel.objects.get_or_create(
            user=request.user,
            resource=resource_score_log.resource
        )

        if (updates['upvote']):
            if (not resource_user_log.upvoted):
                resource_score_log.upvote = F('upvote') + 1
                resource_user_log.upvoted = True

                if (resource_user_log.downvoted):
                    resource_user_log.downvoted = False
                    resource_score_log.downvote = F('downvote') - 1
            else:
                resource_user_log.upvoted = False
                resource_score_log.upvote = F('upvote') - 1

        if (updates['downvote']):
            if (not resource_user_log.downvoted):
                resource_score_log.downvote = F('downvote') + 1
                resource_user_log.downvoted = True

                if (resource_user_log.upvoted):
                    resource_user_log.upvoted = False
                    resource_score_log.upvote = F('upvote') - 1
            else:
                resource_user_log.downvoted = False
                resource_score_log.downvote = F('downvote') - 1

        if (updates['reported']):
            if (not resource_user_log.reported):
                try:
                    report_reason = FlagReason.objects.get(pk=request.data.get('reason')) 
                    flagModel.objects.create(resource=resource_score_log.resource, user=request.user, reason=report_reason)
                    resource_user_log.reported = True
                except FlagReason.DoesNotExist:
                    pass
            else:
                try:
                    flagModel.objects.get(resource=resource_score_log.resource, user=request.user).delete()
                except flagModel.DoesNotExist:
                    pass
                resource_user_log.reported = False
            resource_score_log.reported = flagModel.objects.filter(resource=resource_score_log.resource).count()

        resource_user_log.save()
        resource_user_log.refresh_from_db()

        resource_score_log.save()
        resource_score_log.refresh_from_db()

        resource_log_serializer = scoreLogSerializer(resource_score_log)
        user_log_serializer = userLogSerializer(resource_user_log)
        return Response({
            'resource_log': resource_log_serializer.data,
            'user_log': user_log_serializer.data
        })

class FlagReasons(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = FlagReason.objects.all()
    serializer_class = FlagReasonSerializer

class ResourceReports(APIView):
    def get_models(self, request):
        resource_type = self.request.query_params.get('resource_type')

        if (resource_type == 'article'):
            return Articles, ArticleFlagLogs
        elif (resource_type == 'media'):
            return Media, MediaFlagLogs
        else:
            raise Http404

    def get(self, request):
        resourceModel, flagLogsModel = self.get_models(request)
        pk = self.request.query_params.get('pk')

        resource = resourceModel.objects.get(pk=pk)
        reasons = FlagReason.objects.get_queryset()

        response = {}

        for reason in reasons:
            response[reason.reason] = flagLogsModel.objects.filter(resource=resource, reason=reason).count()

        return Response(response)
