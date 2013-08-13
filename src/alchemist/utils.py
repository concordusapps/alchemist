# -*- coding: utf-8 -*-
import io
import ipaddress


def build_database_uri(testing=False, **kwargs):
    # Resolve the expanded form into a database URI.
    o = io.StringIO()

    # Build key names and get properly.
    def key(name):
        if testing and ('test_' + name) in kwargs:
            return 'test_' + name

        return name

    # Add the designated engine.
    o.write(kwargs[key('engine')])
    o.write('://')

    # Add the username.
    user = False
    if key('user') in kwargs:
        o.write(kwargs[key('user')])
        user = True

    elif key('username') in kwargs:
        o.write(kwargs[key('username')])
        user = True

    # Add the password.
    if user:
        if key('pass') in kwargs:
            o.write(':')
            o.write(kwargs[key('pass')])

        elif key('password') in kwargs:
            o.write(':')
            o.write(kwargs[key('password')])

    # Add the hostname.
    null = 'localhost' if user else None
    hostname = kwargs.get(key('host'), kwargs.get(key('hostname'), null))
    if hostname:
        if user:
            # Write the user / host separator.
            o.write('@')

        ipaddr = True
        try:
            # Check if this is an ip address.
            ipaddress.ip_address(hostname)
            o.write('[')

        except ValueError:
            # This is not.
            ipaddr = False

        # Write out the hostname.
        o.write(hostname)
        if ipaddr:
            o.write(']')

    # Add the port.
    if key('port') in kwargs:
        o.write(':')
        o.write(str(kwargs[key('port')]))

    # Add the name.
    o.write('/')

    # Default a testing name if we have one.
    name = None
    if testing and 'test_name' not in kwargs:
        if kwargs[key('engine')] == 'sqlite':
            name = ':memory:'

        else:
            name = 'test_' + kwargs['name']

    if name is None:
        name = kwargs[key('name')]

    o.write(name)

    # Return our constructed URI.
    return o.getvalue()
