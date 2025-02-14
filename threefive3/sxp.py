"""
sxp.py
home of the SuperXmlParser class

"""

from xml.sax.saxutils import unescape
from .xml import strip_ns, iter_attrs


CHILD_NODES = [
        "Program",
        "SpliceTime",
        "DeliveryRestrictions",
        "SegmentationUpid",
        "BreakDuration",
    ]

class SuperXmlParser:
    """
    The Super Xml Parser
    """
    def __init__(self,child_nodes=CHILD_NODES):
        """
        __init__  allows you to specify child nodes
        
        My thinking was, since I know which ones are
        child nodes, why  not specify them?
        """
        self.child_nodes=child_nodes

    def _split_attrs(self, node):
        node = node.replace("='", '="').replace("' ", '" ')
        attrs = [x for x in node.split(" ") if "=" in x]
        return attrs

    def mk_attrs(self, node):
        """
        mk_attrs parses the current node for attributes
        and stores them in self.stuff[self.active]
        """
        attrs = {}
        try:
            attrs = self._split_attrs(node)
            parsed = {
                x.split('="')[0]: unescape(x.split('="')[1].split('"')[0])
                for x in attrs
            }
            attrs = iter_attrs(parsed)
        except:
            pass
        return attrs

    def mk_tag(self, data):
        """
        mk_tag parse out the
        next available xml tag from data
        """
        tag = data[1:].split(" ", 1)[0].split(">", 1)[0]
        return strip_ns(tag.strip())

    def _vrfy_sp(self, sp):
        if sp and sp[0] not in ["!", "/"]:
            return True
        return False

    def _mk_value(self, sp):
        return sp.split(">")[1].replace("\n", "").strip()

    def _assemble(self, sp):
        return {
            "name": self.mk_tag(sp),
            "attrs": self.mk_attrs(sp),
            "this": self._mk_value(sp),
            "children": [],
        }

    def fu(self, exemel):
        """
        fu slice up exemel into data chunks.
        """
        results = []
        exemel = exemel.replace("\n", "").strip()
        splitted = exemel.split("<")
        for sp in splitted:
            if self._vrfy_sp(sp):
                x = self._assemble(sp)
                if x["name"] in self.child_nodes:
                    results[-1]["children"].append(x)
                else:
                    results.append(x)
        return results
