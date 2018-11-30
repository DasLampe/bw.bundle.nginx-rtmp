pkg = {
    'nginx': {},
}

directories = {
    '/etc/nginx/modules-available': {},
    '/etc/nginx/modules-enabled': {},
}

files = {
    '/etc/nginx/modules-available/rtmp_module.conf': {
        'content': 'load_module modules/ngx_rtmp_module.so;',
    },
}

symlinks = {
    '/etc/nginx/modules-enabled/rtmp_module.conf': {
        'target': '/etc/nginx/modules-available/rtmp_module.conf',
        'needs': [
            'pkg:nginx',
            'action:install_rtmp_module',
            'file:/etc/nginx/modules-available/rtmp_module.conf',
        ],
        'triggers': [
            'svc_systemd:nginx:reload',
        ],
    },
}

if node.metadata.get('nginx-rtmp', {}).get('build_from_source', True):
    downloads = {
        '/tmp/build_module.sh': {
            'url': 'https://hg.nginx.org/pkg-oss/raw-file/1.15.7-1/build_module.sh',
            'sha256': 'e279b038147355522a4a60a1f2e3c75bc14d8e0861e004151d2683f24cb1e7cb',
        },
    }

    actions = {
        'build_rtmp_module': {
            'command': 'sh /tmp/build_module.sh -y -o /tmp/ -n rtmp -v $(nginx -v 2>&1 | cut -d "/" -f2) https://github.com/sergey-dryabzhinsky/nginx-rtmp-module.git',
            'needs': [
                'pkg:nginx',
                'download:/tmp/build_module.sh',
            ],
        },
    }

    if node.os in node.OS_FAMILY_REDHAT:
        actions['build_rtmp_module']['unless'] = 'rpm -qa nginx-module-rtmp | grep $(nginx -v 2>&1 | cut -d "/" -f2)' # Has already this version installed

        actions['install_rtmp_module'] = {
            'command': 'rpm -i /tmp/nginx-module-rtmp-$(nginx -v 2>&1 | cut -d "/" -f2)-*.rpm',
            'needs': [
                'pkg:nginx',
                'action:build_rtmp_module',
            ],
            'unless': 'rpm -qa nginx-module-rtmp | grep $(nginx -v 2>&1 | cut -d "/" -f2)',
        }

    if node.os in node.OS_FAMILY_DEBIAN:
        actions['build_rtmp_module']['unless'] = 'dpkg -s nginx-module-rtmp | grep "Version" | grep "$(nginx -v 2>&1 | cut -d \'/\' -f2)"' # Has already this version installed

        actions['install_rtmp_module'] = {
            'command': 'dpkg --install /tmp/nginx-module-rtmp_$(nginx -v 2>&1 | cut -d "/" -f2)-*.deb',
            'needs': [
                'pkg:nginx',
                'action:build_rtmp_module',
            ],
            'unless': 'dpkg -s nginx-module-rtmp | grep "Version" | grep "$(nginx -v 2>&1 | cut -d \'/\' -f2)"',
        }
else:
    # Install from repo
    pkg['nginx-module-rtmp'] = {
        'installed': True,
    }


files["/etc/nginx/stream.d/rtmp.conf"] = {
    'source': 'etc/nginx/stream.d/rtmp.conf',
    'content_type': 'mako',
    'context': {
        'config': node.metadata.get('nginx-rtmp', {}),
    },
    'triggers': [
        'svc_systemd:nginx:reload',
    ],
    'needs': [
        'pkg:nginx',
    ]
}
