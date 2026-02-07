from .wb import WB


class Item:
    def __init__(self, data: dict, wb=None, commit=False, summary=None):
        if wb is None:
            self.wb = WB()
        else:
            self.wb = wb

        self.data = data
        self.identify_data()

        if "qid" in data and data["qid"]:
            self.item = self.wb.wbi.item.get(data["qid"])
        else:
            self.item = self.wb.wbi.item.new()

        if "label" in data and data["label"]:
            self.item.labels.set("en", data["label"])

        if "aliases" in data and data["aliases"]:
            if not isinstance(data["aliases"], list):
                data["aliases"] = [data["aliases"]]
            self.item.aliases.set(
                "en", data["aliases"], action_if_exists=self.wb.wbi_enums.ActionIfExists.REPLACE_ALL
            )

        if "description" in data and data["description"]:
            self.item.descriptions.set("en", data["description"][:250])

        if "claims" in data:
            for claim_data in data["claims"]:
                self.process_claim(claim_data)

        if commit:
            self.response = self.item.write(summary=summary)
            if "item_talk_cache" in data and data["item_talk_cache"]:
                item_talk_page = self.wb.mw_site.pages[f"Item_talk:{self.response.id}"]
                item_talk_page.save(
                    data["item_talk_cache"], summary="cached content to item talk page"
                )

    def _property_type(self, pid=None, prop_name=None):
        if pid is None:
            pid = self.wb.props[prop_name]["property"]
        p = self.wb.wbi.property.get(pid)
        if not p:
            raise ValueError(f"Property {prop_name} not found")
        return str(p.datatype).split(".")[-1]

    def item_data_template(self):
        item_data_template = {
            "qid": "",
            "label": "",
            "description": "",
            "aliases": [""],
            "claims": [
                {
                    "property_name": "",
                    "value": "",
                    "qualifiers": [{"property_name": "", "values": [""], "replace": True}],
                    "references": [{"property_name": "", "values": [""], "replace": True}],
                }
            ],
        }

        return item_data_template

    def get_value(self, statement):
        value = statement.mainsnak.datavalue["value"]
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            for k in ["id", "text", "time", "amount"]:
                if k in value:
                    return value[k]
        return None

    def identify_data(self):
        # Pre-process claims for PID and property data type values
        # Build statement containers for claims, qualifiers, and references
        if "claims" in self.data:
            for claim_obj in self.data["claims"]:
                claim_obj["pid"] = self.wb.props[claim_obj["property_name"]]["property"]
                claim_obj["p_datatype"] = self._property_type(claim_obj["pid"])
                if not claim_obj["value"].startswith("SPECIAL:"):
                    if claim_obj["p_datatype"] == "TIME":
                        claim_obj["value"] = self.wb.wb_dt(claim_obj["value"])
                    elif claim_obj["p_datatype"] == "QUANTITY":
                        claim_obj["value"] = int(claim_obj["value"])
                claim_obj["statement"] = self.build_statement(
                    pid=claim_obj["pid"],
                    p_datatype=claim_obj["p_datatype"],
                    value=claim_obj["value"],
                )
                if "qualifiers" in claim_obj and claim_obj["qualifiers"]:
                    for q_obj in claim_obj["qualifiers"]:
                        q_obj["pid"] = self.wb.props[q_obj["property_name"]]["property"]
                        q_obj["p_datatype"] = self._property_type(q_obj["pid"])
                        if not isinstance(q_obj["values"], list):
                            q_obj["values"] = [q_obj["values"]]
                        q_obj["statements"] = []
                        for value in q_obj["values"]:
                            if not value.startswith("SPECIAL:"):
                                if q_obj["p_datatype"] == "TIME":
                                    value = self.wb.wb_dt(value)
                                elif q_obj["p_datatype"] == "QUANTITY":
                                    value = int(value)
                            q_obj["statements"].append(
                                self.build_statement(
                                    pid=q_obj["pid"], p_datatype=q_obj["p_datatype"], value=value
                                )
                            )
                if "references" in claim_obj and claim_obj["references"]:
                    for r_obj in claim_obj["references"]:
                        r_obj["pid"] = self.wb.props[r_obj["property_name"]]["property"]
                        r_obj["p_datatype"] = self._property_type(r_obj["pid"])
                        if not isinstance(r_obj["values"], list):
                            r_obj["values"] = [r_obj["values"]]
                        r_obj["statements"] = []
                        for value in r_obj["values"]:
                            if not value.startswith("SPECIAL:"):
                                if r_obj["p_datatype"] == "TIME":
                                    value = self.wb.wb_dt(value)
                                elif r_obj["p_datatype"] == "QUANTITY":
                                    value = int(value)
                            r_obj["statements"].append(
                                self.build_statement(
                                    pid=r_obj["pid"], p_datatype=r_obj["p_datatype"], value=value
                                )
                            )

    def build_statement(self, pid=None, prop_name=None, value=None, p_datatype=None):
        if p_datatype is None:
            p_datatype = self._property_type(prop_name)

        statement = None
        snak_type = self.wb.wbi_enums.WikibaseSnakType.KNOWN_VALUE
        if value is not None and value == "SPECIAL:UNKNOWN_VALUE":
            snak_type = self.wb.wbi_enums.WikibaseSnakType.UNKNOWN_VALUE
        elif value is not None and value == "SPECIAL:NO_VALUE":
            snak_type = self.wb.wbi_enums.WikibaseSnakType.NO_VALUE

        if pid is None:
            pid = self.wb.props[prop_name]["property"]

        if p_datatype == "ITEM":
            statement = self.wb.datatypes.Item(prop_nr=pid, snaktype=snak_type)
        elif p_datatype == "URL":
            statement = self.wb.datatypes.URL(prop_nr=pid, snaktype=snak_type)
        elif p_datatype == "EXTERNALID":
            statement = self.wb.datatypes.ExternalID(prop_nr=pid, snaktype=snak_type)
        elif p_datatype == "STRING":
            statement = self.wb.datatypes.String(prop_nr=pid, snaktype=snak_type)
        elif p_datatype == "MONOLINGUALTEXT":
            statement = self.wb.datatypes.MonolingualText(
                prop_nr=pid, language="en", snaktype=snak_type
            )
        elif p_datatype == "TIME":
            statement = self.wb.datatypes.Time(prop_nr=pid, snaktype=snak_type)
        elif p_datatype == "QUANTITY":
            statement = self.wb.datatypes.Quantity(prop_nr=pid, snaktype=snak_type)

        if value is not None and not value.startswith("SPECIAL:"):
            statement.set_value(value)

        return statement

    def process_claim(self, claim_data: dict):
        claim = None
        new_claim = False

        item_claims = self.item.claims.get(claim_data["pid"])
        claim = next((c for c in item_claims if self.get_value(c) == claim_data["value"]), None)

        if not claim:
            new_claim = True
            claim = claim_data["statement"]

        if "qualifiers" in claim_data and claim_data["qualifiers"]:
            for q_data in claim_data["qualifiers"]:
                if q_data["replace"]:
                    remove_qualifiers = []
                    for qualifier in claim.qualifiers:
                        if qualifier.get_json()["property"] == q_data["pid"]:
                            remove_qualifiers.append(qualifier)
                    for q in remove_qualifiers:
                        try:
                            claim.qualfiers.remove(q)
                        except (AttributeError, ValueError):
                            claim.qualifiers.clear()

                for statement in q_data["statements"]:
                    claim.qualifiers.add(statement)

        if "references" in claim_data and claim_data["references"]:
            for r_data in claim_data["references"]:
                if r_data["replace"]:
                    remove_references = []
                    for reference in claim.references:
                        if reference.get_json()["property"] == r_data["pid"]:
                            remove_references.append(reference)
                    for r in remove_references:
                        try:
                            claim.qualfiers.remove(r)
                        except (AttributeError, ValueError):
                            claim.qualifiers.clear()

                for statement in r_data["statements"]:
                    claim.references.add(statement)

        if new_claim:
            self.item.claims.add(claim)
