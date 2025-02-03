"""It turns owl ontolgie into yaml file using owlready2"""

import enum
from itertools import chain, cycle, groupby
from collections import namedtuple
from operator import itemgetter
from pathlib import Path
from typing import Annotated
import yaml

from loguru import logger
from owlready2 import get_ontology
from owlready2.entity import ThingClass, Restriction
import typer


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
    def __init__(self,
                 ontology_file: Path, 
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
        self.ontology = parser(str(ontology_file))
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
    
    def get_class_hierarchy(self) -> dict[str, dict[str, list[str] | str] | None]:
        """AI is creating summary for get_class_hierarchy

        Returns:
            dict[str, list[str]]: [description]
        """
        classes = dict()
        for c in self.ontology.classes():
            if c.is_a is not None:
                classes[c.__name__] = {'ctype': 'class', 'parents': [], 'restrictions': [], 'debug': []}
                for a in c.is_a:
                    match a:
                        case ThingClass():
                            classes[c.__name__]['parents'].append(a.name)
                        case Restriction():
                            classes[c.__name__]['restrictions'].append(str(a))
                        case _:
                            classes[c.__name__]['debug'].append(str(a))
                            case={'child': str(c), 'parent': str(a)}
                            logger.info(f"No compliant case to debug: {case}")
        return classes

    def get_instance_hierarchy(self) -> dict[str, dict[str, list[str] | str] | None]:
        """AI is creating summary for get_class_hierarchy

        Returns:
            dict[str, list[str]]: [description]
        """
        return {c.name: {'ctype': 'individual',
                         'parents':list(map(lambda x: getattr(x, 'name', None), c.is_a)),
                         'restrictions': None,
                         'debug': None} for c in self.ontology.individuals()}

    def to_yaml(self) -> str:
        """
        AI is creating summary for to_yaml

        Returns:
            str: [description]
        """
        return yaml.dump(self(), default_flow_style=False, sort_keys=False, indent=4, width=80)

    def __call__(self, *args, **kwds) -> dict:
        """AI is creating summary for __call__

        Returns:
            dict: [description]
        """
        data_properties = self.get_properties_by_class(PropertyType.DATA_PROPERTIES)
        nodes = [{'name': k, 'properties': data_properties.get(k, None)} 
                 for k, v in self.get_properties_attributes(PropertyType.CLASS).items()]
        relationships = self.get_properties_attributes(PropertyType.OBJECT_PROPERTIES)
        entities = self.get_class_hierarchy()
        instances = self.get_instance_hierarchy()
        entities.update(instances)
        return {'nodes': nodes, 'relationships': list(relationships.values()), 'hierarchy': entities}

def main(
    input_owl: Annotated[Path, typer.Option(exists=True, dir_okay=False, file_okay=True, help="OWL file to parse.")],

    output_yaml: Annotated[
        Path, typer.Option(exists=False, dir_okay=True, file_okay=True, help="Output file to write YAML.")
    ]):
    """
    Takes a OWL ontology and serializes it to a YAML.
    """
    logger.info(f"Parsing OWL file: {input_owl}")
    
    onto = OntologyAnalyzer(input_owl)
    with open(output_yaml, "w") as ofh:
            logger.info(f"Writing YAML to: {output_yaml}")
            ofh.write(onto.to_yaml())
    logger.info("Graph created successfully.")


if __name__ == "__main__":
    typer.run(main)
