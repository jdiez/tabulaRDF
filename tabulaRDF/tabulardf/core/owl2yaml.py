
import enum
from itertools import chain, cycle, groupby
from collections import namedtuple
from operator import itemgetter
import yaml

from owlready2 import get_ontology


# property_data = namedtuple('PropertyData', ['name', 'iri', 'domain', 'range'])
property_data = namedtuple('PropertyData', ['name', 'iri', 'source', 'target'])
class_data = namedtuple('ClassData', ['name', 'iri', 'is_a'])


@enum.unique
class PropertyType(str, enum.Enum):
    """AI is creating summary for PropertyType

    Args:
        str ([type]): [description]
        enum ([type]): [description]
    """
    OBJECT_PROPERTIES = 'object_properties'
    DATA_PROPERTIES = 'data_properties'
    ANNOTATION_PROPERTIES = 'annotation_properties'
    CLASS = 'class'


class OntologyAnalyzer:
    """AI is creating summary for 
    """
    def __init__(self, ontology_file: str, 
                 parser: callable=lambda x: get_ontology(x).load(),
                 property_data_nt: namedtuple = property_data,
                 class_data_nt: namedtuple = class_data) -> None:
        """AI is creating summary for __init__

        Args:
            ontology_file (str): [description]
            parser (callable, optional): [description]. Defaults to lambdax:get_ontology(x).load().
            property_data_nt (namedtuple, optional): [description]. Defaults to property_data.
            class_data_nt (namedtuple, optional): [description]. Defaults to class_data.
        """
        self.class_data_nt = class_data_nt
        self.property_data_nt = property_data_nt
        self.ontology = parser(ontology_file)
        self.classes = sorted({c.name: c for c in self.ontology.classes()})
        self.individuals = sorted({i.name: i for i in self.ontology.individuals()})
        self.individuals_different = sorted({i.name: i for i in self.ontology.different_individuals()})
        self.data_properties = sorted({dp.name: dp for dp in self.ontology.data_properties()})
        self.object_properties = sorted({op.name: op for op in self.ontology.object_properties()})

    def get_properties_by_class(self, name: PropertyType) -> dict[str, list[str]]:
        """AI is creating summary for get_properties

        Args:
            name (PropertyType): [description]

        Returns:
            dict[str, list[str]]: [description]
        """
        data = [list(zip([i.name for i in p.domain], 
                         cycle([self.property_data_nt(p.name, 
                                              p.iri,
                                              list(map(lambda x: x.__name__, p.domain)), 
                                              list(map(lambda x: x.__name__, p.range))
                                              )._asdict()])))
                                              for p in getattr(self.ontology, name)() if len(p.domain) > 0]
        data = sorted(chain(*data), key=itemgetter(0))
        res = {key: [val[1] for val in group] for key, group in groupby(data, key=lambda x: x[0])}
        return res
    
    def get_properties_attributes(self, name: PropertyType) -> dict[str, list[str]]:
        """AI is creating summary for get_properties_attributes

        Args:
            name (PropertyType): [description]

        Returns:
            dict[str, list[str]]: [description]
        """
        match name:
            case PropertyType.CLASS:
                return {c.name: self.class_data_nt(c.name, 
                                           c.iri, 
                                           list(map(lambda x: str(x), c.is_a))
                                           )._asdict()
                                           for c in self.ontology.classes()}
            case PropertyType.DATA_PROPERTIES | PropertyType.OBJECT_PROPERTIES:
                return {op.name: self.property_data_nt(op.name,
                                               op.iri, 
                                               list(map(lambda x: str(x.name), op.domain)), 
                                               list(map(lambda x: str(x.name), op.range))
                                               )._asdict()
                                               for op in getattr(self.ontology, name)() if len(op.domain) > 0}
            case _:
                raise ValueError("Invalid property type")

    def __call__(self, *args, **kwds) -> dict:
        """AI is creating summary for __call__

        Returns:
            dict: [description]
        """
        data_properties = self.get_properties_by_class(PropertyType.DATA_PROPERTIES)
        nodes = [{'name': k, 'properties': data_properties.get(k, None)} 
                 for k, v in self.get_properties_attributes(PropertyType.CLASS).items()]
        relationships = self.get_properties_attributes(PropertyType.OBJECT_PROPERTIES)
        return {'nodes': nodes,'relationships': list(relationships.values())}


def get_wrapp(ontology_file: str="PizzaTutorialWithDataV2.owl") -> dict:
    """AI is creating summary for get_wrapp

    Args:
        ontology_file (str, optional): [description]. Defaults to "PizzaTutorialWithDataV2.owl".

    Returns:
        dict: [description]
    """
    onto=OntologyAnalyzer(ontology_file)()
    print(yaml.dump(onto, default_flow_style=False, sort_keys=False, indent=4, width=80))
    return onto


if __name__ == "__main__":
    get_wrapp()
