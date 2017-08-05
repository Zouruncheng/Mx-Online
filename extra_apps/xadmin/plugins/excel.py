# coding:utf-8

import xadmin
from xadmin.views import BaseAdminPlugin, ListAdminView
from django.template import loader


class ListImportExcelPlugin(BaseAdminPlugin):
    """
    excel 导入
    """
    import_excel = False

    def init_request(self, *args, **kwargs):
        return bool(self.import_excel)

    def block_top_toolbar(self, context, nodes):
        nodes.append(loader.render_to_string('xadmin/excel/model_list.top_toolbar.import.html', context_instance=context))

xadmin.site.register_plugin(ListImportExcelPlugin, ListAdminView)
