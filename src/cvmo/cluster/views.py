from django.shortcuts import render

#
# Views
#


def show_new(request):
    return render(
        request,
        "cluster/new.html", {}
    )


def show_edit(request, cluster_id):
    return render(
        request,
        "cluster/new.html", {}
    )


def show_deploy(request, cluster_id):
    return render(request, "cluster/deploy.html", {})

#
# Actions
#


def save(request):
    pass


def delete(request, cluster_id):
    pass
