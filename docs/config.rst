Configuration
=============

.. envvar:: APP__NAME
    :type: :obj:`str`

.. confval:: APP__DEBUG
    :type: :obj:`bool`
    :default: False

.. confval:: APP__ROOT
    :type: :obj:`pathlib.Path`
    :default: /app-root

.. confval:: APP__ENTRY
    :type: :obj:`flask.Flask` | :obj:`typing.Callable[[], flask.Flask]`
