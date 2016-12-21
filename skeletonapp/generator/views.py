from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import ProcessedSkeleton
import json

def edit_skeleton(request, skid):
    """
    Edit the skeleton
    """

    template = loader.get_template('edit_skeleton.html')
    skeleton = get_object_or_404(ProcessedSkeleton, pk=skid)
    skeleton.pos_ent = json.loads(skeleton.possible_entries)
    current_head = skeleton.skeleton.split()[0][1:]
    after_head = " ".join(skeleton.skeleton.split()[1:])

    changed=False
    if request.method == 'POST':
        role = request.POST.get("role", None)
        if role in skeleton.possible_entries:
            skeleton.skeleton = "(" + role + " "+after_head
            skeleton.skeleton_type = ProcessedSkeleton.MANUAL_SEL
            skeleton.save()
            current_head = role
            changed=True

    context = {
        "skeleton": skeleton,
        "after_head": after_head,
        "current_head": current_head,
        "changed": changed,
    }

    return HttpResponse(template.render(context, request))
