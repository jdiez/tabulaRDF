"""
It converts a YAML file to a RDF graph.
"""
import copy
import json
import re
import uuid
from functools import partial
from pathlib import Path

import pandas as pd
import rdflib
import typer
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from ruamel.yaml import YAML
from typing_extensions import Annotated, Any, Callable, Generator

# Define custom progress bar
progress_bar = Progress(
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)

FORMAT_READERS = {
    "csv": pd.read_csv,
    "excel": pd.read_excel,
    "parquet": pd.read_parquet,
}


class FactoryRDFstatements:
    """Generates RDF statements for a given class."""

    def __init__(
        self,
        class_name: str,
        config: dict[str, Any],
        prefixes_name: str | None = "prefixes",
        attributes_name: str | None = "attributes",
        multisep: str | None = ";",
    ) -> None:
        """Init method for FactoryRDFstatements.

        Args:
            config (dict[str, Any]): [description]
            prefixes_name (str, optional): [description]. Defaults to 'prefixes'.
            attributes_name (str, optional): [description]. Defaults to 'attributes'.
        """
        self.class_name = class_name
        self.config = config
        self.prefixes = config.get(prefixes_name)
        self.attributes = config.get(attributes_name)
        self.multisep = multisep
        self.class_dict = {
            k: v
            for k, v in self.config.items()
            if k not in (prefixes_name, attributes_name)
        }
        self.class_col = self.class_dict["colname"]
        self._dispatcher()

    def __repr__(self) -> str:
        """Object representation method.

        Returns:
            str: [description]
        """
        return json.dumps(
            {
                "class_name": self.class_name,
                "class_dict": self.class_dict,
                "prefixes": self.prefixes,
                "attributes": self.attributes,
            }
        )

    def _dispatcher(self) -> None:
        """_attr_set_ dispatch method."""
        self._dict = {}
        for val in self.attributes.values():
            self._dict[val["colname"]] = partial(
                self._predicate_definition_statement, val["domain"], val["range"]
            )
        self._dict[self.class_dict["colname"]] = self._class_definition_statement

    def _get_classuri(self, v) -> str:
        """AI is creating summary for _get_classuri

        Args:
            v ([type]): [description]

        Returns:
            str: [description]
        """
        _subject_uri: str = self._resolve_prefix(self.class_dict["subject_uri"]) + v
        if self.class_dict["create_uuid"]:
            _subject_uri: str = self._resolve_prefix(
                self.class_dict["subject_uri"]
            ) + str(uuid.uuid5(uuid.NAMESPACE_URL, _subject_uri))
        return _subject_uri

    def _class_definition_statement(self, v) -> None:
        """AI is creating summary for _class_definition_statement

        Args:
            v ([type]): [description]

        Returns:
            [type]: [description]
        """
        _subject_uri = rdflib.URIRef(v)
        _predicate_uri = rdflib.URIRef(self._resolve_prefix("rdf:type"))
        _object_uri = rdflib.URIRef(self._resolve_prefix(self.class_dict["class_uri"]))
        return (_subject_uri, _predicate_uri, _object_uri)

    def _predicate_definition_statement(
        self,
        cv: str,
        k: str,
        v: str,
        create_uuid: bool = False,
        literal_prefix: str = "http://www.w3.org/2001/XMLSchema",
    ) -> None:
        """AI is creating summary for _predicate_definition_statement

        Args:
            cv (str): [description]
            k (str): [description]
            v (str): [description]
            literal_prefix (str, optional): [description]. Defaults to 'http://www.w3.org/2001/XMLSchema'.

        Returns:
            [type]: [description]
        """
        _subject_uri = rdflib.URIRef(cv)
        _predicate_uri = rdflib.URIRef(self._resolve_prefix(k["domain"]))  # create uuid
        _object_uri = self._resolve_prefix(k["range"])  # this one could be a literal.
        if _object_uri.startswith(literal_prefix):
            _object_uri = rdflib.Literal(v, datatype=rdflib.term.URIRef(_object_uri))
        else:
            if create_uuid == True:
                _object_uri: str = _object_uri + str(
                    uuid.uuid5(uuid.NAMESPACE_URL, _object_uri + v)
                )
            else:
                _object_uri = _object_uri + v
            _object_uri = rdflib.URIRef(_object_uri)
        return (_subject_uri, _predicate_uri, _object_uri)

    def _resolve_prefix(
        self,
        uri: str,
        pattern: str = r"^(?P<base>\w+)?(?P<sep>:)?(?P<nspace>[_a-zA-Z0-9#\/]+)?$",
    ) -> str:
        """AI is creating summary for _resolve_prefix

        Args:
            uri (str): [description]
            pattern (str, optional): [description]. Defaults to r'(?P<base>\w+)?(?P<sep>:)?(?P<nspace>\w+)?'.

        Raises:
            ValueError: [description]

        Returns:
            str: [description]
        """
        res = re.match(pattern, uri).groupdict()
        match res:
            case {"base": None, "sep": None, "nspace": None}:
                return f'{self.prefixes["base"]}'
            case {"base": str(), "sep": None, "nspace": None}:
                return f'{self.prefixes[res["base"]]}'
            case {"base": None, "sep": str(), "nspace": str()}:
                return f'{self.prefixes["base"]}{res["nspace"]}'
            case {"base": str(), "sep": str(), "nspace": str()}:
                return f'{self.prefixes[res["base"]]}{res["nspace"]}'
            case _:
                raise ValueError(f"URI {uri} is not valid.")

    def __call__(self, record: dict[str, str]) -> tuple[str]:
        """AI is creating summary for __call__

        Args:
            record (dict[str, str]): [description]

        Returns:
            tuple[str]: [description]
        """
        attrs = {k: v for k, v in self.attributes.items() if k != self.class_col}
        # Multiple columns?
        if self.multisep in self.class_col:
            assert self.class_dict["create_uuid"] == True, ValueError(
                f"{self.class_col} is not unique."
            )
            vals = self.class_col.split(self.multisep)
            mcol = set([record[i] for i in vals])
            res = "_".join(mcol)
            klass_uri = self._get_classuri(res)
        else:
            klass_uri = self._get_classuri(record[self.class_col])
            # yield self._class_definition_statement(record[self.class_col])
            res_1 = self._class_definition_statement(klass_uri)
            yield res_1
        for _, value in attrs.items():
            # yield self._predicate_definition_statement(record[self.class_col], value, record[value['colname']])
            if value.get("create_uuid"):
                create_uuid = True
            else:
                create_uuid = False
            res_2 = self._predicate_definition_statement(
                klass_uri, value, record[value["colname"]], create_uuid=create_uuid
            )
            yield res_2


class GraphDF:
    """ """

    def __init__(self, df: pd.DataFrame, metadata: dict) -> None:
        """AI is creating summary for __init__

        Args:
            df (pd.DataFrame): [description]
            metadata (dict): [description]
        """
        self.df = df
        self.metadata = metadata

    def get_classes(self) -> Generator:
        """AI is creating summary for get_classes

        Returns:
            list[dict[str, dict[str, Any]]]: [description]
        """
        for c, v in self.metadata["classes"].items():
            v["prefixes"] = self.metadata["prefixes"]
            yield c, v

    def get_class(self, class_name: str) -> dict[str, dict[str, Any]]:
        """AI is creating summary for get_classes

        Returns:
            list[dict[str, dict[str, Any]]]: [description]
        """
        try:
            metadata = self.metadata["classes"][class_name]
        except KeyError:
            raise ValueError(f"Class {class_name} is not defined.")
        return metadata

    def set_df_uuids(
        df: pd.DataFrame, id_col: str, index: str, uuid_function: Callable
    ) -> pd.DataFrame:
        """AI is creating summary for set_uuids

        Args:
            df (pd.DataFrame): [description]
            indexes (list[str]): [description]
            uuid_function (Callable): [description]

        Returns:
            pd.DataFrame: [description]
        """
        df[index] = df[id_col].apply(uuid_function)
        return df

    def get_class_dataframe_renamed(
        self, elements: list[dict[str, dict[str, str]]]
    ) -> Generator[str, dict, pd.DataFrame]:
        """AI is creating summary for get_dataframe_renamed

        Args:
            data (pd.DataFrame): [description]
            elements (list[dict[str, dict[str, str]]]): [description]

        Yields:
            Generator[tuple[str, dict, pd.DataFrame]]: [description]
        """
        for k, v in elements.items():  # self.metadata.items()
            odf = self.get_odf(k, v)
            yield k, v, odf

    def get_odf(self, class_name: str, class_metatdata: dict[str, Any]) -> pd.DataFrame:
        """AI is creating summary for get_odf

        Args:
            class_metatdata (dict[str, Any]): [description]

        Returns:
            pd.DataFrame: [description]
        """
        map_table = {
            v["name"]: v["rename"] for c, v in class_metatdata["attributes"].items()
        }
        odf = copy.deepcopy(self.df[map_table.keys()].drop_duplicates())
        # need to check list elements.
        odf.columns = map_table.values()
        odf = self.set_df_uuid(odf, class_metadata["colname"], class_metadata["uuid"])
        return odf


def read_table(
    filename: Path, input_format: str, readers: dict[str, Callable] = FORMAT_READERS
) -> pd.DataFrame:
    """AI is creating summary for read_table

    Args:
        filename (Path): [description]
        input_format (str): [description]
        readers (dict[str, Callable], optional): [description]. Defaults to FORMAT_READERS.

    Returns:
        pd.DataFrame: [description]
    """
    assert input_format in readers.keys(), ValueError(
        f"Input format {input_format} not supported."
    )
    return readers[input_format](filename)


def get_config_colnames(
    config: dict[str, Any],
    prefixes_name: str = "prefixes",
    attributes_name: str = "attributes",
    multicol_sep: str = ";",
) -> list[str]:
    """AI is creating summary for get_config_colnames

    Args:
        config (dict[str, Any]): [description]
        prefixes_name (str, optional): [description]. Defaults to 'prefixes'.
        attributes_name (str, optional): [description]. Defaults to 'attributes'multicol_sep:str=';'.

    Returns:
        list[str]: [description]
    """
    attributes_dict = config[attributes_name]
    class_dict = {
        k: v for k, v in config.items() if k not in (prefixes_name, attributes_name)
    }
    attributes_colnames = [v["colname"] for v in attributes_dict.values()]
    if not multicol_sep in class_dict["colname"]:  # allow multiple index column.
        class_colname = class_dict["colname"]
        attributes_colnames += [class_colname]
    else:
        class_colname = class_dict["colname"].split(multicol_sep)
        attributes_colnames += class_colname
    return list(set(attributes_colnames))


def merge_graphs(graphs: list[rdflib.Graph]) -> rdflib.Graph:
    """AI is creating summary for merge_graphs

    Args:
        graphs (list): [description]

    Returns:
        Graph: [description]
    """
    from functools import reduce

    return reduce(lambda g1, g2: g1.union(g2), graphs)


def parse_ruyaml(filename: str | Path, _typ="safe") -> dict[str, Any]:
    """
    Assumes that the file is a yaml file.
    YAML is parsed and returned as a dict.

    Args:
        filename (str | Path): _description_
        _typ (str, optional): _description_. Defaults to 'safe'.

    Returns:
        dict[str, Any]: _description_
    """
    filename = Path(filename) if isinstance(filename, str) else filename
    try:
        yaml = YAML(typ=_typ)
        result = yaml.load(filename)
    except Exception as e:
        raise ValueError(f"Could not read {filename} as YAML: {str(e)}")
    else:
        return result


def generate_graph(
    table: pd.DataFrame,
    struct: dict[str, Any],
    bg: rdflib.Graph,
    factory: Callable = FactoryRDFstatements,
) -> rdflib.Graph:
    """AI is creating summary for generate_graph

    Args:
        table (pd.DataFrame): [description]
        struct (dict[str, Any]): [description]

    Returns:
        rdflib.Graph: [description]
    """
    gg = GraphDF(table, struct)
    classes = gg.get_classes()
    with progress_bar as p):
        for _klass in p.track(classes):
            _name, _config = _klass
            frs = factory(_name, _config)
            ids = (
                table[get_config_colnames(_config)]
                .drop_duplicates()
                .to_dict(orient="records")
            )
            for id in ids:
                idsl = list(frs(id))
                for i in idsl:
                    bg.add(i)
    return bg


def main(
    table: Annotated[Path, typer.Option(exists=True, dir_okay=False, file_okay=True, help="Table file. Default: CSV.")],
    config: Annotated[Path, typer.Option(exists=True, dir_okay=False, file_okay=True, help="YAML config file.")],
    output_file: Annotated[
        Path, typer.Option(exists=False, dir_okay=True, file_okay=True, help="Output file to write RDF.")
    ]
    | None = None,
    input_format: Annotated[str, typer.Option(help="Table format.")] = "csv",
    output_format: Annotated[
        str, typer.Option(help="Serialization format.")
    ] = "turtle",
):
    """
    Takes a YAML file and serializes it to a RDF graph.
    Defaults to turtle serialization.
    """
    import sys
    # track different progress bars. (https://rich.readthedocs.io/en/stable/progress.html#transient-progress)
    df = read_table(table, input_format)
    struct = parse_ruyaml(config)
    bg = generate_graph(df, struct, factory=FactoryRDFstatements, bg=rdflib.Graph())
    rdf_output = bg.serialize(format="turtle")
    if output_file is not None:
        with open(output, "w") as ofh:
            ofh.write(rdf_output)
        sys.exit("Graph created successfully.")
    else:
        sys.stdout.buffer.write(rdf_output)


if __name__ == "__main__":
    typer.run(main)
