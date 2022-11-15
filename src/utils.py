import logging
from dataclasses import dataclass

import betterproto
from typing import Dict

import proto.tendermint.types as ttypes

PROTO_PATH = "proto"


@dataclass(eq=False, repr=False)
class Any(betterproto.Message):
    type_url: str = betterproto.string_field(1)
    value: betterproto.Message = betterproto.message_field(2)

    def to_dict(
        self,
        casing: betterproto.Casing = betterproto.Casing.SNAKE,
        include_default_values: bool = False,
    ) -> Dict[str, object]:
        raw_dict = super().to_dict(casing, include_default_values)
        dict_: Dict[str, object] = {}
        type_url = casing("type_url").rstrip("_")  # type: ignore
        if type_url in raw_dict:
            dict_["@type"] = raw_dict[type_url]
        value = casing("value").rstrip("_")  # type: ignore
        dict_.update(raw_dict.get(value, {}))
        return dict_


def getClassForType(message: dict):

    # from https://stackoverflow.com/a/7281397
    def load_class(dottedpath):
        """Load a class from a module in dotted-path notation.

        E.g.: load_class("package.module.class").

        Based on recipe 16.3 from Python Cookbook, 2ed., by Alex Martelli,
        Anna Martelli Ravenscroft, and David Ascher (O'Reilly Media, 2005)

        """
        assert dottedpath is not None, "dottedpath must not be None"
        splitted_path = dottedpath.split(".")
        modulename = ".".join(splitted_path[:-1])
        classname = splitted_path[-1]
        try:
            try:
                module = __import__(modulename, globals(), locals(), [classname])
            except ValueError:  # Py < 2.5
                if not modulename:
                    module = __import__(
                        __name__.split(".")[0], globals(), locals(), [classname]
                    )
        except ImportError:
            # properly log the exception information and return None
            # to tell caller we did not succeed
            logging.exception(
                "Could not load class %s" " because an exception occurred", dottedpath
            )
            return None
        try:
            return getattr(module, classname)
        except AttributeError:
            logging.exception(
                "Could not load class %s" " because the class was not found", dottedpath
            )
            return None

    return load_class(PROTO_PATH + "." + message["@type"][1:])


def createAnyFromDict(message):
    type_url = "/" + message["@type"][1:]
    return Any(
        type_url=type_url,
        value=getClassForType(message)().from_dict(message).SerializeToString(),
    )


def extractGenesisValidatorsFromGenesis(genesis_json):
    validators = [
        ttypes.Validator().from_dict(val_json)
        for val_json in genesis_json.get("validators", [])
    ]

    return validators
