import json
import logging
import os
import re

import docker

import dataset
import bcrypt
from invoke import run, task

BOOTSTRAP_IMAGE_CHEIP = "codenvy/che-ip:nightly"


@task
def update(ctx):
    print "***************************initial*********************************"
    ctx.run("env", pty=True)
    pub_ip = _geonode_public_host_ip()
    print "Public Hostname or IP is {0}".format(pub_ip)
    pub_port = _geonode_public_port()
    print "Public PORT is {0}".format(pub_port)
    adminsos_pwd = _sos_admin_pwd(
        os.getenv(
            "SOS_ADMIN_PASSWORD",
            "password"
        )
    )
    print "Admin SOS password bcrypt hashed is {0}".format(adminsos_pwd)
    envs = {
        "public_fqdn": "{0}:{1}".format(pub_ip, pub_port),
        "public_host": "{0}".format(pub_ip),
        "hashed_pwd": "{0}".format(adminsos_pwd),
        "override_fn": "$HOME/.override_env"
    }
    ctx.run("echo export GEOSERVER_PUBLIC_LOCATION=\
http://{public_fqdn}/geoserver/ >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export SERVICE_SOSURL=\
http://{public_fqdn}/observations/sos >> {override_fn}".format(
        **envs
    ), pty=True)
    ctx.run("echo export SOS_ADMIN_PASSWORD={hashed_pwd} >> {override_fn}".format(
        **envs
    ), pty=True)


@task
def updatedb(ctx):
    print "********************update configuration*************************"
    ctx.run("cp -rup $CATALINA_HOME/webapps/observations/configuration.db \
$CATALINA_HOME/webapps/observations/configuration.db.backup", pty=True)
    _prepare_configuration_database()


def _docker_host_ip():
    client = docker.from_env()
    ip_list = client.containers.run(BOOTSTRAP_IMAGE_CHEIP,
                                    network_mode="host"
                                    ).split("\n")
    if len(ip_list) > 1:
        print("Docker daemon is running on more than one \
address {0}".format(ip_list))
        print("Only the first address:{0} will be returned!".format(
            ip_list[0]
        ))
    else:
        print("Docker daemon is running at the following \
address {0}".format(ip_list[0]))
    return ip_list[0]


def _container_exposed_port(component, instname):
    client = docker.from_env()
    ports_dict = json.dumps(
        [c.attrs["Config"]["ExposedPorts"] for c in client.containers.list(
            filters={
                "label": "org.geonode.component={0}".format(component),
                "status": "running"
            }
        ) if "{0}".format(instname) in c.name][0]
    )
    for key in json.loads(ports_dict):
        port = re.split("/tcp", key)[0]
    return port


def _geonode_public_host_ip():
    gn_pub_hostip = os.getenv("GEONODE_LB_HOST_IP", "")
    if not gn_pub_hostip:
        gn_pub_hostip = _docker_host_ip()
    return gn_pub_hostip


def _geonode_public_port():
    gn_pub_port = os.getenv("GEONODE_LB_PORT", "")
    if not gn_pub_port:
        gn_pub_port = _container_exposed_port(
            "nginx",
            os.getenv("GEONODE_INSTANCE_NAME", "starterkit")
        )
    return gn_pub_port


def _sos_admin_pwd(pwd):
    hashed = bcrypt.hashpw(pwd, bcrypt.gensalt())
    if bcrypt.checkpw(pwd, hashed):
        print("Initial input password {0} matches!").format(
            pwd
        )
        return hashed
    else:
        print("Initial input password {0} Does not Match :(").format(
            pwd
        )
        raise EnvironmentError


def _prepare_dict_identifiers():

    pub_ip = _geonode_public_host_ip()
    print "Public Hostname or IP is {0}".format(pub_ip)
    pub_port = _geonode_public_port()
    print "Public PORT is {0}".format(pub_port)

    default_administrator_user = {
        "id": 1,
        "username": os.getenv(
            "SOS_ADMIN_USERNAME",
            "admin"
        ),
        "password": os.getenv(
            "SOS_ADMIN_PASSWORD",
            "$2a$10$vbp9aXCDMP/fXwEsqe/1.eon44mMdUyC4ub2JfOrkPfaer5ciLOly"
        )
    }

    strings_settings_identifiers = {
        "serviceProvider.phone": os.getenv(
            "SERVICEPROVIDER_PHONE",
            "na"
        ),
        "serviceProvider.city": os.getenv(
            "SERVICEPROVIDER_CITY",
            "na"
        ),
        "serviceProvider.state": os.getenv(
            "SERVICEPROVIDER_STATE",
            "na"
        ),
        "serviceProvider.postalCode": os.getenv(
            "SERVICEPROVIDER_POSTALCODE",
            "na"
        ),
        "serviceProvider.country": os.getenv(
            "SERVICEPROVIDER_COUNTRY",
            "na"
        ),
        "serviceProvider.name": os.getenv(
            "SERVICEPROVIDER_NAME",
            "na"
        ),
        "serviceProvider.individualName": os.getenv(
            "SERVICEPROVIDER_INDIVIDUALNAME",
            "na"
        ),
        "serviceProvider.positionName": os.getenv(
            "SERVICEPROVIDER_POSITIONNAME",
            "na"
        ),
        "serviceProvider.address": os.getenv(
            "SERVICEPROVIDER_ADDRESS",
            "na"
        ),
        "inspire.namespace": os.getenv(
            "SERVICEPROVIDER_NAMESPACE",
            "na"
        ),
        "serviceProvider.email": os.getenv(
            "SERVICEPROVIDER_EMAIL",
            "na"
        ),
        "misc.defaultOfferingPrefix": os.getenv(
            "MISC_DEFAULTOFFERINGPREFIX",
            "offering:"
        ),
        "service.transactionalToken": os.getenv(
            "SOS_TRANSACTIONAL_AUTHORIZATION_TOKEN",
            "changeme"
        ),
        "service.transactionalAllowedIps": os.getenv(
            "TRANSACTIONAL_ALLOWED_IPS",
            ""
        ),
        "service.transactionalAllowedProxies": os.getenv(
            "TRANSACTIONAL_ALLOWED_PROXIES",
            ""
        )
    }

    uri_settings_identifiers = {
        "service.sosUrl": os.getenv(
            "SERVICE_SOSURL", "na"
        ),
        "serviceProvider.site": os.getenv(
            "SERVICEPROVIDER_SITE", "na"
        ),
        "inspire.metadataUrl.url": os.getenv(
            "INSPIRE_METADATA_URL", "na"
        )
    }

    boolean_settings_identifiers = {
        " service.security.transactional.active": os.getenv(
            "TRANSACTIONAL_ACTIVE", 1
        )
    }

    return strings_settings_identifiers, uri_settings_identifiers, boolean_settings_identifiers, default_administrator_user


def _prepare_configuration_database():
    strings, uri, boolean, default_admin = _prepare_dict_identifiers()

    try:
        db = dataset.connect(
            'sqlite:///' + os.path.join(
                os.path.join(
                    os.environ['CATALINA_HOME'],
                    'webapps/observations'
                ),
                'configuration.db'
            )
        )
        tb_administrator_user = db['administrator_user']
        # treat strings dict as tuple to filter and update records
        admin_update = default_admin
        tb_administrator_user.update(
            admin_update,
            ['id']
        )

        tb_strings_settings = db['strings_settings']
        # treat strings dict as tuple to filter and update records
        for item_string in strings.items():
            tb_strings_settings.update(
                dict(
                    identifier=item_string[0],
                    value=item_string[1]
                ),
                ['identifier']
            )

        tb_uri_settings = db['uri_settings']
        # treat uri dict as tuple to filter and update records
        for item_uri in uri.items():
            tb_uri_settings.update(
                dict(
                    identifier=item_uri[0],
                    value=item_uri[1]
                ),
                ['identifier']
            )

        tb_boolean_settings = db['boolean_settings']
        # treat uri dict as tuple to filter and update records
        for item_boolean in boolean.items():
            tb_boolean_settings.update(
                dict(
                    identifier=item_boolean[0],
                    value=item_boolean[1]
                ),
                ['identifier']
            )

    except OperationalError as e:
        raise
