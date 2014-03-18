import pprint
import json
import base64
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from querystring_parser import parser
from .forms import ClusterForm, EC2Form, QuotaForm, ElastiqForm
from ..context.models import ContextDefinition, ContextStorage

#
# Views
#


def show_new(request):
    return _show_cluster_def(request, {})


def show_test(request):
    return _show_cluster_def(request, {
        "elastiq": {
            "n_jobs_per_vm": 4,
            "estimated_vm_deploy_time_s": 600,
            "batch_plugin": "condor"
        },
        "quota": {
            "min_vms": 2,
            "max_vms": ""
        },
        "ec2": {
            "api_url": "http://openstack.cern.ch:8773/services/Cloud",
            "api_version": "",
            "aws_access_key_id": "6bebac94cd4b4c0da1af747ae98468e5",
            "aws_secret_access_key": "de5587ddc50f422683e1873e0875061b",
            "image_id": "ami-000001f3",
            "key_name": "glestari",
            "flavour": "m1.small"
        },
        "cluster": {
            "id": "",
            "name": "Hello world",
            "description": "",
            "master_context_id": "32c2291ae49a4d889217488a404a96a1",
            "worker_context_id": "99aa82a1b14f494088d4afa459ca8515"
        }
    })


def show_edit(request, cluster_id):
    return _show_cluster_def(request, {})


def show_deploy(request, cluster_id):
    return render(request, "cluster/deploy.html", {})

#
# Actions
#


def save(request):
    # Validate request
    resp = _validate_for_save(request)
    if isinstance(resp, HttpResponse):
        return resp

    # Prepare context
    eq_plg = _render_elastq_plugin(resp)
    print eq_plg
    return HttpResponse(eq_plg, content_type="text/normal")


def delete(request, cluster_id):
    pass

#
# Helpers
#

def _extract_user_data(context_id):
    pass

def _render_elastq_plugin(resp):
    """
    Given the clean data from the cluster form it returns a string, the
    elastiq_setup amiconfig plugin settings.
    """
    plg = "[elastiq_setup]\n"
    plg += "elastiq_n_jobs_per_vm=%d\n" \
        % resp["elastiq"].get("elastiq_n_jobs_per_vm", 4)
    plg += "elastiq_n_jobs_per_vm=%d\n" \
        % resp["elastiq"].get("elastiq_n_jobs_per_vm", 4)
    plg += "elastiq_estimated_vm_deploy_time_s=%d\n" \
        % resp["elastiq"].get("estimated_vm_deploy_time_s", 600)
    plg += "elastiq_batch_plugin=%s\n" \
        % resp["elastiq"].get("batch_plugin", "htcondor")

    plg += "quota_min_vms=%d\n" \
        % resp["quota"].get("min_vms", 2)
    v = resp["quota"].get("max_vms", None)
    if v:
        plg += "quota_max_vms=%d\n" % v

    plg += "ec2_api_url=%s\n" \
        % resp["ec2"]["api_url"]
    plg += "ec2_aws_access_key_id=%s\n" \
        % resp["ec2"]["aws_access_key_id"]
    plg += "ec2_aws_secret_access_key=%s\n" \
        % resp["ec2"]["aws_secret_access_key"]
    plg += "ec2_image_id=%s\n" \
        % resp["ec2"]["image_id"]
    v = resp["ec2"].get("api_version", None)
    if v:
        plg += "ec2_api_version=%s\n" % v
    v = resp["ec2"].get("key_name", None)
    if v:
        plg += "ec2_key_name=%s\n" % v
    v = resp["ec2"].get("flavour", None)
    if v:
        plg += "ec2_flavour=%s\n" % v

    wc = ContextStorage.objects.get(id=resp["cluster"]["worker_context_id"])
    wc_data = base64.b64encode(wc.data)
    plg += "ec2_user_data_b64=%s\n" % wc_data

    return plg


def _validate_for_save(request):
    """
    Validates the HttpRequest. It uses the forms defined in forms.py to
    check all the fields and runs some additional checks. It returns
    an HttpResponse instance if request is invalid and the dictionary of clean
    date otherwise.
    """
    data = parser.parse(request.POST.urlencode())
    clean_data = {}

    # Cluster section
    cluster_f = ClusterForm(data.get("cluster", {}))
    if not cluster_f.is_valid():
        for label, msg in cluster_f.errors_list:
            messages.error(request, "Cluster %s: %s" % (label, msg))
        return _show_cluster_def(request, data)
    clean_data["cluster"] = cluster_f.clean()

    # Check that contexts belong to user or is public
    for context_field_code in ["master_context_id", "worker_context_id"]:
        c = ContextDefinition.objects.get(
            id=clean_data["cluster"][context_field_code]
        )
        if not c.public and c.owner != request.user:
            messages.error(
                request,
                "Context %s: is not public and does not belong to you" % (c.id)
            )
            return _show_cluster_def(request, data)

    # elastiq section
    elastiq_f = ElastiqForm(data.get("elastiq", {}))
    if not elastiq_f.is_valid():
        for label, msg in elastiq_f.errors_list:
            messages.error(request, "Elastq %s: %s" % (label, msg))
        return _show_cluster_def(request, data)
    clean_data["elastiq"] = elastiq_f.clean()

    # EC2 section
    ec2_f = EC2Form(data.get("ec2", {}))
    if not ec2_f.is_valid():
        for label, msg in ec2_f.errors_list:
            messages.error(request, "EC2 %s: %s" % (label, msg))
        return _show_cluster_def(request, data)
    clean_data["ec2"] = ec2_f.clean()

    # Quota section
    quota_f = QuotaForm(data.get("quota", {}))
    if not quota_f.is_valid():
        for label, msg in quota_f.errors_list:
            messages.error(request, "Quota %s: %s" % (label, msg))
        return _show_cluster_def(request, data)
    clean_data["quota"] = quota_f.clean()

    return clean_data


def _show_cluster_def(request, data={}):
    """
    Given the HttpRequest and an optional dictionary, it renders the cluster
    definition form page. Useful for the empty form of the new cluster,
    for cluster editing and for re-rendering failed forms when client-side
    validation does not work.
    """
    if "cluster" in data:
        for context_code in ["master_context", "worker_context"]:
            cid = data["cluster"].get("%s_id" % context_code, None)
            if cid:
                try:
                    c = ContextDefinition.objects.get(id=cid)
                    data["cluster"]["%s_json" % context_code] = json.dumps({
                        "id": c.id,
                        "name": c.name,
                        "description": c.description,
                        "owner": c.owner.username
                    })
                except ContextDefinition.DoesNotExist:
                    del data["cluster"]["%s_id" % context_code]
                    data["cluster"]["%s_json" % context_code] = json.dumps({})

    return render(
        request,
        "cluster/new.html",
        data
    )
