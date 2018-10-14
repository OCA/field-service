##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Common pieces of the workflow architecture.
"""

from zope.interface import implementer
from zope.component.interfaces import ObjectEvent

from Products.CMFCore.interfaces import IWorkflowActionEvent
from Products.CMFCore.interfaces import IActionWillBeInvokedEvent
from Products.CMFCore.interfaces import IActionRaisedExceptionEvent
from Products.CMFCore.interfaces import IActionSucceededEvent


class WorkflowException(Exception):

    """ Exception while invoking workflow.
    """


class ObjectDeleted(Exception):

    """ Raise to tell the workflow tool that the object has been deleted.

    Swallowed by the workflow tool.
    """
    def __init__(self, result=None):
        self._r = result

    def getResult(self):
        return self._r


class ObjectMoved(Exception):

    """ Raise to tell the workflow tool that the object has moved.

    Swallowed by the workflow tool.
    """
    def __init__(self, new_ob, result=None):
        self._ob = new_ob  # Includes acquisition wrappers.
        self._r = result

    def getResult(self):
        return self._r

    def getNewObject(self):
        return self._ob


# Events

@implementer(IWorkflowActionEvent)
class WorkflowActionEvent(ObjectEvent):

    def __init__(self, object, workflow, action):
        ObjectEvent.__init__(self, object)
        self.workflow = workflow
        self.action = action


@implementer(IActionWillBeInvokedEvent)
class ActionWillBeInvokedEvent(WorkflowActionEvent):
    pass


@implementer(IActionRaisedExceptionEvent)
class ActionRaisedExceptionEvent(WorkflowActionEvent):
    pass

    def __init__(self, object, workflow, action, exc):
        WorkflowActionEvent.__init__(self, object, workflow, action)
        self.exc = exc


@implementer(IActionSucceededEvent)
class ActionSucceededEvent(WorkflowActionEvent):

    def __init__(self, object, workflow, action, result):
        WorkflowActionEvent.__init__(self, object, workflow, action)
        self.result = result
