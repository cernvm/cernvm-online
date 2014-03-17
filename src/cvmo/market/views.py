from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q
from django.core.urlresolvers import reverse
from cvmo.market.models import MarketplaceGroup, MarketplaceContextVotes, \
    MarketplaceContextEntry
from cvmo.context.models import ContextDefinition
from cvmo.core.utils.views import render_error, render_confirm, \
    uncache_response, msg_info, set_memory, msg_error, msg_confirm, \
    redirect_memory, get_memory
from PIL import Image
import json


def list(request):
    templates = range(40)

    groups = MarketplaceGroup.objects.all()

    return render_to_response('market/marketplace_list.html', {
        'templates': templates,
        'groups': groups
    }, RequestContext(request))


def vote_ajax(request):

    # Validate request
    if not 'id' in request.GET:
        return render_error(request, 400)
    if not 'vote' in request.GET:
        return render_error(request, 400)

    # Handle vote
    fID = request.GET['id']
    fVote = request.GET['vote']

    # Check vote
    rank = 0
    if fVote == 'up':
        rank = 1
    else:
        rank = 0

    # Fetch / create per-user, per-entry record
    try:
        o = MarketplaceContextVotes.objects.get(
            user=request.user, entry__id=fID)
    except:
        o = MarketplaceContextVotes()
        o.user = request.user
        try:
            o.entry = MarketplaceContextEntry.objects.get(id=fID)
        except:
            return render_error(request, 404)

    # Update vote
    o.vote = rank
    o.save()

    # Update context rank
    rank = update_context_rank(fID)

    # Return the current entry
    return uncache_response(
        HttpResponse(
            json.dumps({'id': fID, 'rank': rank}),
            content_type="text/plain"
        )
    )


def list_ajax(request):

    # Validate request
    if not 'group' in request.GET:
        return render_error(request, 400)
    if not 'query' in request.GET:
        return render_error(request, 400)
    if not 'offset' in request.GET:
        return render_error(request, 400)

    # Fetch some helpful variables from the request
    fGroup = request.GET['group']
    fQuery = request.GET['query']
    fOffset = int(request.GET['offset'])

    # Extract tags from the string and build the more
    # complex query
    args = [Q(group__id=fGroup)]
    qargs = None
    qstring = ""
    parts = fQuery.split(" ")
    for p in parts:

        # Inclusive tag
        if p[0:1] == "+":
            tag = "|" + p[1:] + "|"
            print "La: %s" % tag
            if qargs == None:
                qargs = Q(tags__contains=tag)
            else:
                qargs = qargs | Q(tags__contains=tag)

        # Exclusive tag
        elif p[0:1] == "-":
            tag = "|" + p[1:] + "|"
            print "Lalo: %s" % tag
            args.append(~Q(tags__contains=tag))

        # Regular keyword
        else:
            if qstring:
                qstring += " "
            qstring += p

    # If we have inclusive tags, add them now
    if qargs != None:
        args.append(qargs)

    # Append string query
    if qstring:
        args.append(Q(context__name__contains=qstring))

    # Fetch items
    items_per_batch = 20
    items = []
    db_items = MarketplaceContextEntry.objects.filter(
        *args).order_by('-rank')[fOffset:]
    num_items = len(db_items)
    cur_item = 0

    for i in db_items:
        items.append({
            'id': i.id,
            'label': i.context.name,
            'icon': i.icon.url,
            'details': i.details,
            'description': i.context.description,
            'uid': i.context.id,
            'owner': i.context.owner.username,
            'tags': i.tags[1:-1].split("|"),
            'rank': i.rank,
            'encrypted': not not i.context.key
        })
        cur_item += 1
        if cur_item >= items_per_batch:
            break

    # Check if we have more items
    has_more = 0
    if num_items > items_per_batch:
        has_more = 1

    # Build response
    data = {
        'offset': fOffset + items_per_batch,
        'more': has_more,
        'items': items
    }

    # Return filtered responses
    return uncache_response(
        HttpResponse(json.dumps(data), content_type="text/plain")
    )

#
# CONTEXT MARKETPLACE FUNCTIONS
#


def publish(request, context_id):

    # Try to find the context
    try:
        context = ContextDefinition.objects.get(id=context_id)
    except:
        msg_error(request, "Context with id " +
                  context_id + " is not defined!")
        return redirect("dashboard")

    # Check if context belongs to calling user
    if request.user.id != context.owner.id:
        msg_error(request, "Context with id " +
                  context_id + " does not belong to you!")
        return redirect("dashboard")

    # Check if this entry is already there
    if MarketplaceContextEntry.objects.filter(context=context).exists():
        msg_info(request, "This context already exists in the marketplace!")
        return redirect('dashboard')

    # Render values
    return uncache_response(
        render_to_response(
            'market/marketplace_publish_ctx.html',
            {
                'groups': MarketplaceGroup.objects.all(),
                'context': context,
                'icons': get_icons(request.user),

                # For redirection with memory
                'values': {
                    'group': get_memory(request, 'group'),
                    'instructions': get_memory(request, 'instructions'),
                    'tags': get_memory(request, 'tags')
                }
            },
            RequestContext(request)
        )
    )


def publish_action(request):

    # Fetch entries
    fContext = request.POST['context']
    fInstructions = request.POST['instructions']
    fTags = request.POST['tags']
    fGroup = request.POST['group']

    # Validate entries
    if not fInstructions:
        msg_error(request, "Please enter some instructions!")
        return redirect_memory(
            reverse("market_publish", kwargs={'context_id': fContext}),
            request
        )

    # Sanitize tags
    tagParts = fTags.split(",")
    tagString = ""
    for t in tagParts:
        t = t.strip()
        if t != "":
            if tagString != "":
                tagString += "|"
            tagString += t.replace(' ', "_").lower()
    tagString = "|" + tagString + "|"

    # Prepare entry
    e = MarketplaceContextEntry()
    e.tags = tagString
    e.details = fInstructions
    e.context = ContextDefinition.objects.get(id=fContext)
    e.group = MarketplaceGroup.objects.get(id=fGroup)

    # Upload image
    if 'icon' in request.FILES:
        icon = request.FILES['icon']
        n = icon.name.lower()
        if not (n.endswith(".jpg") or n.endswith(".jpeg")
                or n.endswith(".png") or n.endswith(".gif")
                or n.endswith(".bmp")):
            msg_error(request, "The uploaded icon file is not an image!")
            return redirect_memory(
                reverse("market_publish", kwargs={'context_id': fContext}),
                request
            )

        e.icon = request.FILES['icon']

    # Or if we already have a previous icon, reuse that
    elif 'prev_icon' in request.POST:
        req_icon = request.POST['prev_icon']
        if user_owns_icon(req_icon, request.user):
            e.icon = req_icon
        else:
            msg_error(request, "You do not have permission to use this icon!")
            return redirect_memory(
                reverse("market_publish", kwargs={'context_id': fContext}),
                request
            )

    else:
        msg_error(request, "No icon was selected!")
        return redirect_memory(
            reverse("market_publish", kwargs={'context_id': fContext}),
            request
        )

    # Save entry (This also stores the uploaded image)
    e.save()

    # The context is also public now
    e.context.public = True
    e.context.save()

    # Now rescale the uploaded icon within 64x64 pixels
    if 'icon' in request.FILES:
        if ((e.icon.width > 84) or (e.icon.height > 84)):
            im = Image.open(e.icon.path)
            im.thumbnail((84, 84), Image.ANTIALIAS)
            im.save(e.icon.path)

    # Go to dashboard
    msg_confirm(request, "Context published successfully!")
    return redirect('dashboard')


def revoke(request, context_id):

    # Try to find the context
    try:
        entry = MarketplaceContextEntry.objects.get(context__id=context_id)
    except:
        msg_error(request, "Context with id " +
                  context_id + " is not in the market!")
        return redirect("dashboard")

    # Check if context belongs to calling user
    if request.user.id != entry.context.owner.id:
        msg_error(request, "Context with id " +
                  context_id + " does not belong to you!")
        return redirect("dashboard")

    # Is it confirmed?
    if ('confirm' in request.GET) and (request.GET['confirm'] == 'yes'):

        # Delete icon if we have the last reference
        if get_icon_usage(entry.icon) == 1:
            try:
                entry.icon.delete()
            except:
                pass

        # The context is also not public any more
        entry.context.public = False
        entry.context.save()

        # Delete the specified contextualization entry
        entry.delete()

        # Go to dashboard
        msg_confirm(request, "Context removed successfully!")
        return redirect('dashboard')

    else:
        # Show the confirmation screen
        return render_confirm(
            request, 'Revoke context',
            'Are you sure you want to remove this entry from the marketplace?',
            reverse('market_revoke', kwargs={'context_id': context_id})
            + '?confirm=yes',
            reverse('dashboard')
        )


#
# HELPER FUNCTIONS
#


def get_icons(user):
    """
    Return a set of paths of the icons that the given user has uploaded
    """

    # Prepare response
    ans = []

    # Process contexts
    defs = MarketplaceContextEntry.objects.filter(context__owner=user)
    for e in defs:
        ans.append({'url': e.icon.url, 'name': e.icon.name})

    # Return collected icons
    return ans


def user_owns_icon(path, user):
    """
    Check if the user owns the given icon path
    """

    # Prepare checking array
    ans = []

    # Process contexts
    defs = MarketplaceContextEntry.objects.filter(context__owner=user)
    for e in defs:
        ans.append(e.icon.name)

    # Return collected icons
    return (path in ans)


def get_icon_usage(icon):
    """
    Return the number of rerefeces the given icon has across marketplace
    entries.
    """

    # Prepare response
    ans = 0

    # Process definitions
    defs = MarketplaceContextEntry.objects.filter(icon=icon)
    ans += len(defs)

    # Return number of references
    return ans


def update_context_rank(id):
    """
    Query the user votes and update the given context ID ranking
    """

    # Prepare rank
    rank = 0

    # Get all votes
    votes = MarketplaceContextVotes.objects.filter(entry__id=id)
    for v in votes:
        rank += v.vote

    # Update entry
    entry = MarketplaceContextEntry.objects.get(id=id)
    entry.rank = rank
    entry.save()

    # Return the rank sum
    return rank
