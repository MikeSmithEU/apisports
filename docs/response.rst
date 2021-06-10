Response
========

When calling one of the :ref:`Sports Classes <sports-classes>` methods, you get an
:class:`AbstractResponse <apisports.response.AbstractResponse>` object as result.
Usually you only need the ``ok`` attribute to check if the request succeeded, and
the ``errors()`` and ``error_description()`` methods if there was an error.
If the request succeeded, you can iterate directly over the
:class:`AbstractResponse <apisports.response.AbstractResponse>` object.
In effect, the iteration is delegated to a
:class:`AbstractData <apisports.data.AbstractData>` object, which you can also
access directly by calling the ``data()`` method.

.. automodule:: apisports.response
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __iter__, __len__
