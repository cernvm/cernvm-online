from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from cvmo.context.models import ContextDefinition

#
# Custom validators
#


def validate_context_id(value):
    try:
        ContextDefinition.objects.get(id=value)
    except ContextDefinition.DoesNotExist:
        raise ValidationError("Context with id `%s` does not exist!" % value)

#
# Cluster definition sub-forms
#


class BootstrapForm(forms.Form):

    @property
    def errors_list(self):
        el = []
        for field in self:
            for msg in self[field.name].errors:
                if field.label:
                    el.append((field.label, msg))
                else:
                    el.append((field.name, msg))
        return el


class ClusterForm(BootstrapForm):
    id = forms.IntegerField(required=False)
    name = forms.CharField(max_length=100)
    description = forms.CharField(required=False)
    master_context_id = forms.CharField(
        max_length=64, validators=[validate_context_id],
        label="Master context"
    )
    master_context_pwd = forms.CharField(required=False)
    worker_context_id = forms.CharField(
        max_length=64, validators=[validate_context_id],
        label="Worker context"
    )
    worker_context_pwd = forms.CharField(required=False)


class EC2Form(BootstrapForm):
    api_url = forms.CharField(
        max_length=120,
        validators=[URLValidator()]
    )
    api_version = forms.CharField(required=False)
    aws_access_key_id = forms.CharField(label="AWS access key")
    aws_secret_access_key = forms.CharField(label="AWS secret key")
    image_id = forms.CharField(label="Worker nodes' image")
    flavour = forms.CharField(label="Worker nodes' flavor")
    key_name = forms.CharField(required=False, label="SSH key name")


class QuotaForm(BootstrapForm):
    min_vms = forms.IntegerField(required=False, min_value=0,
                                 label="Min. workers")
    max_vms = forms.IntegerField(required=False, min_value=0,
                                 label="Max. workers")


class ElastiqForm(BootstrapForm):
    BATCH_PLUGINS = [
        ("htcondor", "HTCondor")
    ]
    n_jobs_per_vm = forms.IntegerField(required=False, min_value=1,
                                       label="Amt. of jobs per VM")
    estimated_vm_deploy_time_s = forms.IntegerField(
        required=False, min_value=1,
        label="Estimated VM deployment time"
    )
    check_queue_every_s = forms.IntegerField(required=False, min_value=1,
                                             label="Queue checking interval")
    check_vms_every_s = forms.IntegerField(required=False, min_value=1,
                                           label="VM checking interval")
    waiting_jobs_time_s = forms.IntegerField(required=False, min_value=1,
                                             label="Min. job wait time")
    idle_for_time_s = forms.IntegerField(required=False, min_value=1,
                                         label="Idle time bef. kill")
    batch_plugin = forms.ChoiceField(choices=BATCH_PLUGINS)
