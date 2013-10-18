# -*- coding: utf-8 -*-
from contextlib import contextmanager


@contextmanager
def settings(app, **kwargs):
    """Save current application config and restore after block.

    Allows override with the keyword arguments.
    """
    # Save the current application config to restore.
    _config = dict(app.config)

    # Make requested changes for this scope.
    app.config.update(kwargs)

    yield

    # Restore the previous application config.
    app.config = _config
