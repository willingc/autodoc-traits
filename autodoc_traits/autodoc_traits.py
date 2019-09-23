"""autodoc extension for configurable traits"""
from sphinx.domains.python import PyClassmember
from sphinx.ext.autodoc import AttributeDocumenter
from sphinx.ext.autodoc import ClassDocumenter
from sphinx.util import logging
from traitlets import TraitType
from traitlets import Undefined

LOG = logging.getLogger(__name__)


class ConfigurableDocumenter(ClassDocumenter):
    """Documenter to auto-document a trait with ``config=True``

    *objtype* is 'auto' + objtype as the directive name.
    *directivetype* overrides the default.
    """

    objtype = "configurable"
    directivetype = "class"

    def get_object_members(self, want_all):
        """Add traits with .tag(config=True) to members list
        
        If *want_all* is True, return all members. Else,
        only return the members given by *self.options.members*.
        
        """
        # returns a bool and list of members
        check, members = super().get_object_members(want_all)

        get_traits = (
            self.object.class_own_traits
            if self.options.inherited_members
            else self.object.class_own_traits
        )

        trait_members = []
        for name, trait in sorted(get_traits(config=True).items()):
            # put help in __doc__ where autodoc will look for it
            trait.__doc__ = trait.help
            trait_members.append((name, trait))
        return check, trait_members + members


class TraitDocumenter(AttributeDocumenter):
    """Specialized Documenter subclass for traitlet attributes"""
    objtype = "trait"
    directivetype = "attribute"
    member_order = 1
    priority = 100

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, TraitType)

    def add_directive_header(self, sig):
        default = self.object.get_default_value()
        if default is Undefined:
            default_s = ""
        else:
            default_s = repr(default)
        self.options.annotation = "c.{name} = {trait}({default})".format(
            name=self.format_name(),
            trait=self.object.__class__.__name__,
            default=default_s,
        )
        super().add_directive_header(sig)


def setup(app):
    """Registers the Sphinx extension.

    This does not need to be called directly. Sphinx
    will load the extension if specified in the ``extensions``
    section of ``conf.py``.
    """
    LOG.info('initializing autodoc_traits')
    app.add_autodocumenter(ConfigurableDocumenter)
    app.add_autodocumenter(TraitDocumenter)
