# Copyright: (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

from ansible.module_utils.six import string_types
from ansible.playbook.attribute import FieldAttribute
from ansible.utils.collection_loader import AnsibleCollectionConfig
from ansible.utils.display import Display

display = Display()


def _ensure_default_collection(collection_list=None):
    default_collection = AnsibleCollectionConfig.default_collection

    if collection_list is None:
        collection_list = []

    if default_collection and default_collection not in collection_list:
        collection_list.insert(0, default_collection)

    if collection_list and not any(c in collection_list for c in ('ansible.builtin', 'ansible.legacy')):
        collection_list.append('ansible.legacy')

    return collection_list


class CollectionSearch:

    collections = FieldAttribute(
        isa='list',
        listof=string_types,
        priority=100,
        default=_ensure_default_collection,
        always_post_validate=True,
        static=True,
        extend=True  # Added to support collection inheritance
    )

    def _load_collections(self, attr, ds):
        ds = self.get_validated_value(
            'collections',
            self.fattributes.get('collections'),
            ds,
            None
        )

        collections = _ensure_default_collection(collection_list=ds)
        return collections if collections else None