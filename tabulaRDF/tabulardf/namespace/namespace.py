from rdflib.namespace import Namespace
from rdflib import URIRef


class RDFnamespaces:
    """Class to handle RDF namespaces within the class environment."""

    def __init__(self, **kwds: dict[str, str]) -> None:
        if len(kwds):
            self.__dict__.update({k: Namespace(v) for k,v in kwds.items()})

    def __getattr__(self, name: str) -> Namespace:
        return self.__dict__.get(name)

    def __call__(self, ns:str, val:str | None = None) -> URIRef:
        """AI is creating summary for __call__

        Args:
            ns (str): [description]
            val (str): [description]

        Returns:
            URIref: [description]
        """
        return self.__getattr__(ns)[val]
