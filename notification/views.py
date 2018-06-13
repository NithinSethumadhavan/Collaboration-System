from Community.models import CommunityArticles, CommunityMembership, CommunityGroups, CommunityFeeds
from Group.models import GroupArticles, GroupMembership
from django.contrib.auth.models import Group as Roles
from notifications.signals import notify

def notif_community_subscribe_unsubscribe(request, community, verb):
    notify.send(sender=request.user, actor=request.user, recipient=request.user,
                verb=verb, target=community, description="community_view")

def notif_publishable_article(request,article):
    comm = CommunityArticles.objects.get(article=article)
    publisher_role = Roles.objects.get(name='publisher')
    publishers = CommunityMembership.objects.filter(community=comm.community, role=publisher_role)
    list = []
    for publisher in publishers:
        if article.created_by != publisher.user:
            list.append(publisher.user)

    admin_role = Roles.objects.get(name='community_admin')
    admins = CommunityMembership.objects.filter(community=comm.community, role=admin_role)

    for admin in admins:
        if article.created_by != admin.user:
            list.append(admin.user)

    notify.send(sender=request.user, actor=request.user, recipient=list,
                verb='This article is publishable', target=article,
                description="article_edit")