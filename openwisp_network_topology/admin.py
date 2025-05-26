import swapper
from django import forms
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.db.models import Q
from django.template.response import TemplateResponse
from django.urls import re_path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from flat_json_widget.widgets import FlatJsonWidget

from openwisp_users.multitenancy import (
    MultitenantAdminMixin,
    MultitenantOrgFilter,
    MultitenantRelatedOrgFilter,
)
from openwisp_utils.admin import ReceiveUrlAdmin, UUIDAdmin

from . import settings as app_settings
from .contextmanagers import log_failure
from .visualizer import GraphVisualizerUrls

Link = swapper.load_model("topology", "Link")
Node = swapper.load_model("topology", "Node")
Topology = swapper.load_model("topology", "Topology")


class TimeStampedEditableAdmin(ModelAdmin):
    """
    ModelAdmin for TimeStampedEditableModel
    """

    def __init__(self, *args, **kwargs):
        self.readonly_fields += ("created", "modified")
        super().__init__(*args, **kwargs)


class BaseAdmin(TimeStampedEditableAdmin):
    save_on_top = True

    class Media:
        css = {
            "all": [
                "netjsongraph/css/src/netjsongraph.css",
                "netjsongraph/css/src/netjsongraph-theme.css",
                "netjsongraph/css/lib/jquery-ui.min.css",
                "netjsongraph/css/style.css",
                "netjsongraph/css/admin.css",
            ]
        }
        js = [
            "admin/js/jquery.init.js",
            "netjsongraph/js/lib/jquery-ui.min.js",
            "netjsongraph/js/src/netjsongraph.min.js",
            "netjsongraph/js/strategy-switcher.js",
            "netjsongraph/js/topology-history.js",
            "netjsongraph/js/visualize.js",
        ]


@admin.register(Topology)
class TopologyAdmin(
    MultitenantAdminMixin, GraphVisualizerUrls, UUIDAdmin, ReceiveUrlAdmin, BaseAdmin
):
    model = Topology
    list_display = [
        "label",
        "organization",
        "parser",
        "strategy",
        "published",
        "created",
        "modified",
    ]
    readonly_fields = [
        "uuid",
        "protocol",
        "version",
        "revision",
        "metric",
        "receive_url",
    ]
    list_filter = ["parser", "strategy", MultitenantOrgFilter]
    search_fields = ["label", "id"]
    actions = ["update_selected", "unpublish_selected", "publish_selected"]
    fields = [
        "label",
        "organization",
        "parser",
        "strategy",
        "url",
        "uuid",
        "key",
        "expiration_time",
        "receive_url",
        "published",
        "protocol",
        "version",
        "revision",
        "metric",
        "created",
    ]
    receive_url_name = "receive_topology"
    receive_url_urlconf = app_settings.TOPOLOGY_API_URLCONF
    receive_url_baseurl = app_settings.TOPOLOGY_API_BASEURL
    change_form_template = "admin/topology/topology/change_form.html"

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if not obj:
            # Receive URL cannot be created without an object.
            # Hence, remove the "receive_url" field.
            fields.remove("receive_url")
        return fields

    def get_actions(self, request):
        """
        move delete action to last position
        """
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            delete = actions["delete_selected"]
            del actions["delete_selected"]
            actions["delete_selected"] = delete
        return actions

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        prefix = "admin:{0}_{1}".format(
            self.opts.app_label, self.model.__name__.lower()
        )
        text = _("View topology graph")
        extra_context.update(
            {
                "additional_buttons": [
                    {
                        "type": "button",
                        "url": reverse(
                            "{0}_visualize".format(prefix), args=[object_id]
                        ),
                        "class": "visualizelink",
                        "value": text,
                        "title": "{0} (ALT+P)".format(text),
                    }
                ]
            }
        )
        return super().change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        options = getattr(self.model, "_meta")
        url_prefix = "{0}_{1}".format(options.app_label, options.model_name)
        return [
            re_path(
                r"^visualize/(?P<pk>[^/]+)/$",
                self.admin_site.admin_view(self.visualize_view),
                name="{0}_visualize".format(url_prefix),
            )
        ] + super().get_urls()

    def _message(self, request, rows, suffix, level=messages.SUCCESS):
        if rows == 1:
            prefix = _("1 {0} was".format(self.model._meta.verbose_name))
        else:  # pragma: nocover
            prefix = _(
                "{0} {1} were".format(rows, self.model._meta.verbose_name_plural)
            )
        self.message_user(request, "{0} {1}".format(prefix, suffix), level=level)

    @admin.action(
        description=_("Update selected topologies (FETCH strategy only)"),
        permissions=["change"],
    )
    def update_selected(self, request, queryset):
        items = list(queryset)
        failed = []
        ignored = []
        for item in items:
            if item.strategy == "fetch":
                try:
                    item.update()
                except Exception as e:
                    failed.append("{0}: {1}".format(item.label, str(e)))
                    with log_failure("update topology admin action", item):
                        raise e
            else:
                ignored.append(item)
        # remove item from items if ignored.
        for item in ignored:
            if item in items:
                items.remove(item)
        failures = len(failed)
        successes = len(items) - failures
        total_ignored = len(ignored)
        if successes > 0:
            self._message(request, successes, _("successfully updated"))
        if failures > 0:
            message = _("not updated. %s") % "; ".join(failed)
            self._message(request, failures, message, level=messages.ERROR)
        if total_ignored > 0:
            message = _("ignored (not using FETCH strategy)")
            self._message(request, total_ignored, message, level=messages.WARNING)

    @admin.action(description=_("Publish selected topologies"), permissions=["change"])
    def publish_selected(self, request, queryset):
        rows_updated = queryset.update(published=True)
        self._message(request, rows_updated, _("successfully published"))

    @admin.action(description=_("Unpublish selected items"), permissions=["change"])
    def unpublish_selected(self, request, queryset):
        rows_updated = queryset.update(published=False)
        self._message(request, rows_updated, _("successfully unpublished"))

    def visualize_view(self, request, pk):
        graph_url, history_url = self.get_graph_urls(request, pk)
        context = self.admin_site.each_context(request)
        opts = self.model._meta
        context.update(
            {
                "is_popup": True,
                "opts": opts,
                "change": False,
                "media": self.media,
                "graph_url": graph_url,
                "history_url": history_url,
            }
        )
        return TemplateResponse(request, "admin/topology/visualize.html", context)


class UserPropertiesForm(forms.ModelForm):
    class Meta:
        widgets = {"user_properties": FlatJsonWidget}


class NodeLinkMixin(MultitenantAdminMixin):
    """
    Adds get_queryset class method that enables
    other extensions to override the admin queryset
    """

    readonly_fields = ["readonly_properties"]

    def get_fields(self, request, obj):
        fields = super().get_fields(request, obj)
        if obj:
            return fields
        fields_copy = list(fields)
        fields_copy.remove("organization")
        return fields_copy

    def get_queryset(self, request):
        return self.model.get_queryset(super().get_queryset(request))

    def readonly_properties(self, obj):
        output = ""
        for key, value in obj.properties.items():
            key = key.replace("_", " ").capitalize()
            output += f"<p><strong>{key}</strong>: {value}</p>"
        return mark_safe(output)

    readonly_properties.short_description = _("Properties")


class TopologyFilter(MultitenantRelatedOrgFilter):
    field_name = "topology"
    parameter_name = "topology_id"
    title = _("topology")


@admin.register(Node)
class NodeAdmin(NodeLinkMixin, BaseAdmin):
    model = Node
    form = UserPropertiesForm
    change_form_template = "admin/topology/node/change_form.html"
    list_display = ["get_name", "organization", "topology", "addresses"]
    search_fields = ["addresses", "label", "properties"]
    list_filter = [
        (MultitenantOrgFilter),
        (TopologyFilter),
    ]
    multitenant_shared_relations = ("topology",)
    autocomplete_fields = ("topology",)
    fields = [
        "topology",
        "organization",
        "label",
        "addresses",
        "readonly_properties",
        "user_properties",
        "created",
        "modified",
    ]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        link_model = self.model.source_link_set.field.model
        admin_url = "admin:{0}_link_change".format(self.opts.app_label)
        extra_context.update(
            {
                "node_links": link_model.objects.select_related("source", "target")
                .only("source__label", "target__label", "cost", "status")
                .filter(Q(source_id=object_id) | Q(target_id=object_id)),
                "admin_url": admin_url,
            }
        )
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(Link)
class LinkAdmin(NodeLinkMixin, BaseAdmin):
    model = Link
    form = UserPropertiesForm
    raw_id_fields = ["source", "target"]
    search_fields = [
        "source__label",
        "target__label",
        "source__addresses",
        "target__addresses",
        "properties",
    ]
    list_display = [
        "__str__",
        "organization",
        "topology",
        "status",
        "cost",
        "cost_text",
    ]
    list_filter = [
        "status",
        (MultitenantOrgFilter),
        (TopologyFilter),
    ]
    multitenant_shared_relations = ("topology", "source", "target")
    autocomplete_fields = ("topology",)
    fields = [
        "topology",
        "organization",
        "status",
        "source",
        "target",
        "cost",
        "cost_text",
        "readonly_properties",
        "user_properties",
        "created",
        "modified",
    ]
