
import re
import logging
import base64
import json
import uuid

from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation
from django.conf import settings

from cvmo.core.utils.context import salt_context_key
from cvmo.context.models import ContextStorage, ContextDefinition
from cvmo.webapi.models import WebAPIOneTimeTag
from cvmo.webapi.util.vmcp import VMCPSigner
from cvmo.core.utils import crypt

def vmcp(request):
	"""
	VMCP Response for starting a particular VM
	"""

	# Get a logger
	log = logging.getLogger("cvmo.webapi")

	# Validate request
	if not "tag" in request.GET:
		log.log(logging.ERROR, "`tag` is required")
		raise SuspiciousOperation("`tag` is required")
	if not "cvm_salt" in request.GET:
		log.log(logging.ERROR, "`cvm_salt` is required")
		raise SuspiciousOperation("`cvm_salt` is required")
	if not "cvm_hostid" in request.GET:
		log.log(logging.ERROR, "`cvm_hostid` is required")
		raise SuspiciousOperation("`cvm_hostid` is required")

	# Get one-time tag
	tag = None
	try:
		tag = WebAPIOneTimeTag.objects.get(uuid=request.GET['tag'])
	except WebAPIOneTimeTag.DoesNotExist:
		log.log(logging.ERROR, "The specified tag does not exist")
		raise Http404()

	# Load settings and append missing data
	vmcp_settings = json.loads( tag.payload )
	vmcp_settings['secret'] = "online:%s" % request.GET['cvm_hostid']

	# Sign response
	signer = VMCPSigner( settings.WEBAPI_VMCP_RSA_PRIVATEKEY )
	signed_settings = signer.sign( vmcp_settings, request.GET['cvm_salt'] )

	# If everything was successful so far, delete tag
	tag.delete()

	# Render
	return HttpResponse(json.dumps(signed_settings),
						content_type="text/plain")

def webstart_run(request, tag_id):
	"""
	Webstart run phase
	"""

	# Render the webstart page
	return render(
		request,
		"webapi/webstart.html",
		{
			"tag": tag_id
		}
	)

def webstart_init(request):
	"""
	Webstart init phase
	"""

	# Get a logger
	log = logging.getLogger("cvmo.webapi")

	# Validate request
	if not "context" in request.GET:
		log.log(logging.ERROR, "`context` is required")
		raise SuspiciousOperation("`context` is required")
	if not "config" in request.GET:
		log.log(logging.ERROR, "`config` is required")
		raise SuspiciousOperation("`config` is required")

	############################
	# Render user data
	############################

	# Fetch context
	try:
		ctx = ContextDefinition.objects.get(id=request.GET['context'])
	except ContextDefinition.DoesNotExist:
		raise SuspiciousOperation("`context` is required")

	# Load the rendered context
	try:
		ctx_storage = ContextStorage.objects.get(id=request.GET['context'])
		ctx_storage_data = ctx_storage.data
	except ContextStorage.DoesNotExist:
		return HttpResponse("not-found-rendered",
							content_type="text/plain")

	# If the context is encrypted, prompt the user
	# for the password
	if ctx.key:

		# If we have password, continue
		if "password" in request.POST:

			# POST already contains "unicode" data!
			pwd = request.POST["password"].encode("ascii", "ignore")
			if salt_context_key(ctx.id, pwd) == ctx.key:

				# Descript and un-base64
				m = re.search(r"^ENCRYPTED:(.*)$", ctx_storage_data.data)
				if m is None:
					return HttpResponse("render-format-error",
										content_type="text/plain")
				try:
					user_data = crypt.decrypt(
						base64.b64decode(str(m.group(1))), pwd)
				except:
					return HttpResponse("render-encoding-error",
										content_type="text/plain")

			else:
	
				# Render password prompt with error
				return render(
					request,
					"webapi/password_prompt.html",
					{
						"context": request.GET['context'],
						"config": request.GET['config'],
						"error": "Wrong password. Please try again"
					}
				)

		else:

			# Render password prompt
			return render(
				request,
				"webapi/password_prompt.html",
				{
					"context": request.GET['context'],
					"config": request.GET['config'],
					"error": ""
				}
			)

	else:
			
		# Un-base64
		m = re.search(r"^\s*EC2_USER_DATA\s*=\s*([^\s]*)$", ctx_storage_data, re.M)
		if m is None:
			return HttpResponse("render-format-error",
								content_type="text/plain")
		try:
			user_data = base64.b64decode(str(m.group(1)))
		except:
			return HttpResponse("render-encoding-error",
								content_type="text/plain")

	############################
	# Fetch WebAPI configuration
	############################

	vm_config_id = int(request.GET['config'])
	try:
		vm_config = settings.WEBAPI_CONFIGURATIONS[vm_config_id]
	except IndexError:
		return HttpResponse("not-found-config",
							content_type="text/plain")

	############################
	# Prepare VMCP One-Time Tag
	############################

	# Create VMCP settings
	vmcp_settings = {
		'name'  		: '%s-%s' % ( ctx.name.replace(" ","_"), "".join([random.choice(string.digits + string.letters) for x in range(0,10)]) ),
		'userData' 		: user_data,
		'memory'  		: vm_config['memory'],
		'cpus' 			: vm_config['cpus'],
		'disk' 			: vm_config['disk'],
		'cernvmVersion'	: settings.WEBAPI_UCERNVM_VERSION,
		'flags'			: 0x39
	}

	# Store json config on tag
	tag = WebAPIOneTimeTag(
			payload=json.dumps( vmcp_settings ),
			uuid=uuid.uuid4().hex
			)
	tag.save()

	# Redirect to the HTTP version of webstart_run
	return redirect(
		reverse("webapi_webstart_run", kwargs={"tag_id": tag.uuid})
		)
