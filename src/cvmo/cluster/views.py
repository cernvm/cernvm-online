from django.shortcuts import render_to_response

def show_cluster_new(request):
    return render_to_response("cluster/new.html", {})
