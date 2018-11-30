# Build rtmp-Module for pre-build nginx

```python
'nginx-rtmp': {
    'build_from_source': True, # Better: Use private repo
    'server': {
        'server1:' {
            'listen': '1935',
            'chunk_size': '4096',
            'application': {
                'live': [
                    """
                    [myconfig];
                    """,
                ],
            },
        },
    },
}
```