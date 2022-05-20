from datetime import datetime
from typing import List
from xml.etree.ElementTree import Element, SubElement, parse
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import abort
from info import APP_VERSION
from utils import calendar, month_to_number


def generate_tei_header(mods_metadata: dict) -> Element:
    """
    Generate a TEI header element from Kramerius+ object

    :param mods_metadata:
        {
            'title': str,
            'source': str,
            'physicalDescription': {
                'extent': str
            },
            'author': {
                'type': 'corporate'|'person',
                'name': str,
                'identifier': str
            },
            'originInfo': {
                'publisher': str,
                'date': str,
                'places': [str]
            },
            'identifiers': [
                {
                    'type': str,
                    'value': str
                },
                ...
            ],
            'processed_by': [
                {
                    'identifier': str,
                    'version': str,
                    'from': str,
                    'to': str,
                    'when': str,
                    'label': str
                },
                ...
            ]
        }
    :returns: an XML element with tag `teiHeader`
    """
    if "title" not in mods_metadata:
        abort(400, description="Attribute title is required.")

    tei_header_attrs = {}
    if "source" in mods_metadata:
        tei_header_attrs["corresp"] = mods_metadata["source"]
    tei_header = Element("teiHeader", tei_header_attrs)

    # SubElement fileDesc
    file_desc = SubElement(tei_header, "fileDesc")
    title_stmt = SubElement(file_desc, "titleStmt")
    title = SubElement(title_stmt, "title")
    title.text = mods_metadata["title"]
    if "author" in mods_metadata:
        author = SubElement(title_stmt, "author")
        if "name" in mods_metadata["author"]:
            pers_name = SubElement(author, "orgName" if mods_metadata["author"]["type"] == "corporate" else "persName")
            pers_name.text = mods_metadata["author"]["name"]
        if "identifier" in mods_metadata["author"]:
            idno = SubElement(author, "idno", {"type": "mods:nameIdentifier"})
            idno.text = mods_metadata["author"]["identifier"]

    if "physicalDescription" in mods_metadata and "extent" in mods_metadata["physicalDescription"]:
        extent = SubElement(file_desc, "extent")
        extent.text = mods_metadata["physicalDescription"]["extent"]

    publication_stmt = SubElement(file_desc, "publicationStmt")
    if "originInfo" in mods_metadata:
        if "publisher" in mods_metadata["originInfo"]:
            publisher = SubElement(publication_stmt, "publisher")
            publisher.text = mods_metadata["originInfo"]["publisher"]
        if "places" in mods_metadata["originInfo"]:
            for place in mods_metadata["originInfo"]["places"]:
                pub_place = SubElement(publication_stmt, "pubPlace")
                pub_place.text = place
        if "date" in mods_metadata["originInfo"]:
            date = SubElement(publication_stmt, "date")
            date.text = mods_metadata["originInfo"]["date"]
    if "identifiers" in mods_metadata:
        for idno_type in mods_metadata["identifiers"]:
            idno = SubElement(publication_stmt, "idno", {"type": "mods:" + idno_type["type"]})
            idno.text = idno_type["value"]
    availability = SubElement(publication_stmt, "availability")
    licence = SubElement(availability, "licence", {"resp": "#NameTag"})
    licence.text = "CC BY-NC-SA"
    availability = SubElement(publication_stmt, "availability")
    licence = SubElement(availability, "licence", {"resp": "#UDPipe"})
    licence.text = "CC BY-NC-SA"

    source_desc = SubElement(file_desc, "sourceDesc")
    SubElement(source_desc, "bibl")

    # SubElement encodingDesc
    if "processedBy" not in mods_metadata:
        mods_metadata["processedBy"] = []
    current_date = datetime.now()
    mods_metadata["processedBy"].append({
        "identifier": "TEIConverter",
        "version": APP_VERSION,
        "when": current_date.strftime('%Y-%m-%dT%H:%M:%S')
    })
    encoding_desc = SubElement(tei_header, "encodingDesc")
    for app in mods_metadata["processedBy"]:
        app_info = SubElement(encoding_desc, "appInfo")
        application_attrs = {}
        if "identifier" in app:
            application_attrs["xml:id"] = app["identifier"]
            application_attrs["ident"] = app["identifier"]
        for attr in ["version", "from", "when", "to"]:
            if attr in app:
                application_attrs[attr] = app[attr]
        application = SubElement(app_info, "application", application_attrs)
        label = SubElement(application, "label")
        if "label" in app:
            label.text = app["label"]

    # SubElement profileDesc
    profile_desc = SubElement(tei_header, "profileDesc")
    text_class = SubElement(profile_desc, "textClass")
    class_code = SubElement(text_class, "classCode", {"scheme": "https://ufal.mff.cuni.cz/nametag/2/models"})
    interp_grp = SubElement(class_code, "interpGrp")
    interps = {
        "a": "ČÍSLA JAKO SOUČÁSTI ADRES",
        "ah": "číslo popisné",
        "at": "telefon, fax",
        "az": "PSČ",
        "g": "GEOGRAFICKÉ NÁZVY",
        "gc": "státní útvary",
        "gh": "vodní útvary",
        "gl": "přírodní oblasti / útvary",
        "gq": "části obcí, pomístní názvy",
        "gr": "menší územní jednotky",
        "gs": "ulice, náměstí",
        "gt": "kontinenty",
        "gu": "obce, hrady a zámky",
        "g_": "geografický název nespecifikovaného typu / nezařaditelný do ostatních typů",
        "i": "NÁZVY INSTITUCÍ",
        "ia": "přednášky, konference, soutěže,...",
        "ic": "kulturní, vzdělávací a vědecké instituce, sportovní kluby,...",
        "if": "firmy, koncerny, hotely,...",
        "io": "státní a mezinárodní instituce, politické strany a hnutí, náboženské skupiny",
        "i_": "instituce nespecifikovaného typu / nezařaditelné do ostatních typů",
        "m": "NÁZVY MÉDIÍ",
        "me": "e-mailové adresy",
        "mi": "internetové odkazy",
        "mn": "periodika, redakce, tiskové agentury",
        "ms": "rozhlasové a televizní stanice",
        "n": "ČÍSLA SE SPECIFICKÝM VÝZNAMEM",
        "na": "věk",
        "nc": "číslo s významem počtu",
        "nb": "číslo strany, kapitoly, oddílu, obrázku",
        "no": "číslo s významem pořadí",
        "ns": "sportovní skóre",
        "ni": "itemizátor",
        "n_": "číslo se specifickým významem, jehož typ nebyl vyčleněn jako samostatný / nelze identifikovat",
        "o": "NÁZVY VĚCÍ",
        "oa": "kulturní artefakty (knihy, filmy stavby,...)",
        "oe": "měrné jednotky (zapsané zkratkou)",
        "om": "měny (zapsané zkratkou, symbolem)",
        "op": "výrobky",
        "or": "předpisy, normy,..., jejich sbírky",
        "o_": "názvy nespecifikovaného typu / nezařaditelné do ostatních typů",
        "p": "JMÉNA OSOB",
        "pc": "obyvatelská jména",
        "pd": "titul (pouze zkratkou)",
        "pf": "křestní jméno",
        "pm": "druhé křestní jméno",
        "pp": "náboženské postavy, pohádkové a mytické postavy, personifikované vlastnosti",
        "ps": "příjmení",
        "p_": "jméno osoby nespecifikovaného typu / nezařaditelné do ostatních typů",
        "t": "ČASOVÉ ÚDAJE",
        "td": "den",
        "tf": "svátky a významné dny",
        "th": "hodina",
        "tm": "měsíc",
        "ty": "rok"
    }
    for interp in interps:
        interp_element = SubElement(interp_grp, "interp", {"xml:id": "nametag-" + interp})
        interp_element.text = interps[interp]

    lang_usage = SubElement(profile_desc, "langUsage")
    language = SubElement(lang_usage, "language", {"ident": "cze"})
    language.text = "cze"
    return tei_header


def generate_tei_page(page: dict) -> Element:
    """
    Generate a TEI page element from Kramerius+ object

    :param page:
        {
            'id': str,
            'title': str,
            'source': str,
            'tokens': [
                {
                    'content': str,
                    'nameTagMetadata': str,
                    'linguisticMetadata': {
                        'position': integer,
                        'uPosTag': str,
                        'misc': str,
                        'feats': str,
                        'lemma': str
                    },
                    'altoMetadata': {
                        'height': float,
                        'width': float,
                        'vpos': float,
                        'hpos': float
                    }
                },
                ...
            ]
        }
    :returns: an XML element with tag `div`
    """
    if "id" not in page:
        abort(400, description="Attribute id is required.")
    if "tokens" not in page:
        page["tokens"] = []

    # Create page division with page break
    div = Element("div")
    pb_attrs = {"xml:id": str(page["id"]).replace(":", "-")}
    if "title" in page:
        pb_attrs["n"] = page["title"]
    if "source" in page:
        pb_attrs["corresp"] = page["source"]
    SubElement(div, "pb", pb_attrs)
    p = SubElement(div, "p")

    # Stack
    stack = []

    # Copy tokens
    token_position_in_sentence = None
    for token in page["tokens"]:
        # Prepare token
        if "content" not in token:
            abort(400, description="Attribute `content` is required in all tokens.")
        if "linguisticMetadata" not in token:
            abort(400, description="Attribute `linguisticMetadata` is required in all tokens.")
        if "position" not in token["linguisticMetadata"]:
            abort(400, description="Attribute `position` is required in all tokens' linguistic metadata.")
        check_properties = ["lemma", "uPosTag", "misc", "feats"]
        for prop in check_properties:
            if prop not in token["linguisticMetadata"]:
                token["linguisticMetadata"][prop] = ""

        # Create paragraph for every sentence
        linguistic_metadata = token["linguisticMetadata"]
        if token_position_in_sentence is None or token_position_in_sentence > linguistic_metadata["position"]:
            s = SubElement(p, "s")
            stack = [s]  # Clear the stack
        token_position_in_sentence = linguistic_metadata["position"]

        # Check nameTag info
        name_tags = []
        if "nameTagMetadata" in token:
            name_tags = token["nameTagMetadata"].split("|")

        if len(name_tags) > 0 or len(stack) > 1:
            # Count continued tags
            continued = 1
            for nameTag in name_tags:
                if "I-" in nameTag:
                    continued += 1
            # Removed not continuing tags
            stack = stack[0:continued]
            # For each new group, add new tag to stack
            for nameTag in name_tags:
                if "B-" in nameTag:
                    grp_name = nameTag[2:]
                    if grp_name == "ah" or \
                            grp_name == "na" or \
                            grp_name == "nc" or \
                            grp_name == "nb" or \
                            grp_name == "ns" or \
                            grp_name == "ni" or \
                            grp_name == "n_":
                        grp = SubElement(stack[-1], "num")
                    elif grp_name == "at":
                        grp = SubElement(stack[-1], "num", {"type": "phone"})
                    elif grp_name == "az":
                        grp = SubElement(stack[-1], "num", {"type": "zip"})
                    elif grp_name == "c" or \
                            grp_name == "C":
                        grp = SubElement(stack[-1], "objectName", {"type": "bibliography"})
                    elif grp_name == "gc":
                        grp = SubElement(stack[-1], "placeName", {"ana": "#nametag-" + grp_name})
                        grp = SubElement(grp, "country")
                    elif grp_name == "gh":
                        grp = SubElement(stack[-1], "geogName", {"type": "water"})
                    elif grp_name == "gl":
                        grp = SubElement(stack[-1], "geogName", {"type": "area"})
                    elif grp_name == "gq" or grp_name == "gu":
                        grp = SubElement(stack[-1], "placeName", {"ana": "#nametag-" + grp_name})
                        grp = SubElement(grp, "settlement")
                    elif grp_name == "gr":
                        grp = SubElement(stack[-1], "placeName", {"ana": "#nametag-" + grp_name})
                        grp = SubElement(grp, "region")
                    elif grp_name == "gs":
                        grp = SubElement(stack[-1], "address", {"ana": "#nametag-" + grp_name})
                        grp = SubElement(grp, "street")
                    elif grp_name == "A":
                        grp = SubElement(stack[-1], "address")
                    elif grp_name == "gt":
                        grp = SubElement(stack[-1], "geogName", {"type": "continent"})
                    elif grp_name == "g_":
                        grp = SubElement(stack[-1], "placeName")
                    elif grp_name == "ia" or \
                            grp_name == "o_" or \
                            grp_name == "p_":
                        grp = SubElement(stack[-1], "objectName")
                    elif grp_name == "ic" or \
                            grp_name == "if" or \
                            grp_name == "io" or \
                            grp_name == "i_" or \
                            grp_name == "mn" or \
                            grp_name == "ms":
                        grp = SubElement(stack[-1], "orgName")
                    elif grp_name == "me":
                        grp = SubElement(stack[-1], "email")
                    elif grp_name == "mi":
                        grp = SubElement(stack[-1], "ref", {"target": token["content"]})
                    elif grp_name == "no":
                        grp = SubElement(stack[-1], "num", {"type": "ordinal"})
                    elif grp_name == "oa":
                        grp = SubElement(stack[-1], "objectName", {"type": "artefact"})
                    elif grp_name == "oe" or \
                            grp_name == "om":
                        grp = SubElement(stack[-1], "unit")
                    elif grp_name == "op":
                        grp = SubElement(stack[-1], "objectName", {"type": "product"})
                    elif grp_name == "or":
                        grp = SubElement(stack[-1], "objectName", {"type": "rule"})
                    elif grp_name == "pc":
                        grp = SubElement(stack[-1], "objectName", {"type": "population"})
                    elif grp_name == "pd":
                        grp = SubElement(stack[-1], "abbr")
                    elif grp_name == "pf":
                        grp = SubElement(stack[-1], "forename")
                    elif grp_name == "pm":
                        grp = SubElement(stack[-1], "forename", {"type": "middle"})
                    elif grp_name == "pp" or \
                            grp_name == "P":
                        grp = SubElement(stack[-1], "persName")
                    elif grp_name == "ps":
                        grp = SubElement(stack[-1], "surname")
                    elif grp_name == "t" or \
                            grp_name == "T":
                        grp = SubElement(stack[-1], "date")
                    elif grp_name == "td":
                        try:
                            grp = SubElement(stack[-1], "date", {"when": "---%02d" % int(token["content"])})
                        except ValueError:
                            grp = SubElement(stack[-1], "date")
                    elif grp_name == "tm":
                        month = month_to_number(linguistic_metadata["lemma"])
                        try:
                            grp = SubElement(stack[-1], "date", {"when": "--%02d" % int(month)})
                        except ValueError:
                            grp = SubElement(stack[-1], "date")
                    elif grp_name == "ty":
                        grp = SubElement(stack[-1], "date", {"when": token["content"]})
                    elif grp_name == "tf":
                        grp = SubElement(stack[-1], "date", {"type": "holiday"})
                    elif grp_name == "th":
                        grp = SubElement(stack[-1], "time")
                    else:
                        grp = SubElement(stack[-1], "group", {"type": grp_name})
                    grp.set("ana", "#nametag-" + grp_name)
                    stack.append(grp)

        # Add a token
        tag = "w"
        attrs = {
            "n": str(linguistic_metadata["position"]),
            "pos": linguistic_metadata["uPosTag"],
        }

        # Check if it is a punctuation
        if linguistic_metadata["uPosTag"] == "PUNCT":
            tag = "pc"
            not_space_after = "SpaceAfter=No" in linguistic_metadata["misc"]
            attrs["join"] = "both" if not_space_after else "left"

        # Add optional attributes
        if "feats" in linguistic_metadata:
            attrs["msd"] = linguistic_metadata["feats"]
        if "lemma" in linguistic_metadata:
            attrs["lemma"] = linguistic_metadata["lemma"]
        if "altoMetadata" in token:
            for attr in ["height", "width", "vpos", "hpos"]:
                if attr in token["altoMetadata"]:
                    attrs["alto-"+attr] = str(token["altoMetadata"][attr])

        # Append to text
        w = SubElement(stack[-1], tag, attrs)
        w.text = token["content"]

    # postprocessing
    for grp in div.findall(".//p"):
        children = list(grp)
        if len(children) == 1 and children[0].tag == "s":
            children_of_s = list(children[0])
            if len(children_of_s) == 1 and \
                    children_of_s[0].tag == "objectName" and \
                    children_of_s[0].get("type", "") == "bibliography":
                children[0].remove(children_of_s[0])
                children_of_s[0].tag = "bibl"
                children_of_s[0].attrib.pop("type")
                grp.append(children_of_s[0])
        # TODO Check if parent is S and its parent is P and S contains only this element
        # then remove S and move this element to P
    for grp in div.findall(".//group[@ana='#nametag-P']"):
        children = set(map(lambda e: e.tag, list(grp)))
        children.discard("forename")
        children.discard("placename")
        children.discard("abbr")
        children.discard("w")
        children.discard("pc")
        if len(children) == 0:
            grp.tag = "persName"
            grp.attrib.pop("type")
    for grp in div.findall(".//date[@ana='#nametag-T']"):
        td = grp.find("date[@ana='#nametag-td']")
        tm = grp.find("date[@ana='#nametag-tm']")
        ty = grp.find("date[@ana='#nametag-ty']")
        if td is not None and tm is not None and ty is not None:
            grp.tag = "date"
            date_elements = ["", "", ""]
            for sub in td.iter():
                if sub is not td:
                    sub.set("ana", "#nametag-td")
                    grp.append(sub)
                    if sub.tag == "w":
                        date_elements[2] = sub.attrib["lemma"]
            for sub in tm.iter():
                if sub is not tm:
                    sub.set("ana", "#nametag-tm")
                    grp.append(sub)
                    if sub.tag == "w" and sub.attrib["lemma"].lower() in calendar:
                        date_elements[1] = calendar[sub.attrib["lemma"]]
            for sub in ty.iter():
                if sub is not ty:
                    sub.set("ana", "#nametag-ty")
                    grp.append(sub)
                    if sub.tag == "w":
                        date_elements[0] = sub.attrib["lemma"]
            grp.remove(td)
            grp.remove(tm)
            grp.remove(ty)
            if len(date_elements[1]) == 1:
                date_elements[1] = "0" + date_elements[1]
            if len(date_elements[2]) == 1:
                date_elements[2] = "0" + date_elements[2]
            if len(date_elements[0]) == 4 and len(date_elements[1]) == 2 and len(date_elements[2]) == 2:
                grp.set("when", "-".join(date_elements))
            if len(date_elements[0]) == 0 and len(date_elements[1]) == 2 and len(date_elements[2]) == 2:
                grp.set("when", "-%s-%s" % (date_elements[1], date_elements[2]))
            if len(date_elements[0]) == 0 and len(date_elements[1]) == 0 and len(date_elements[2]) == 2:
                grp.set("when", "---%s" % (date_elements[0]))
            if len(date_elements[0]) == 0 and len(date_elements[1]) == 2 and len(date_elements[2]) == 0:
                grp.set("when", "--%s" % (date_elements[1]))
            if len(date_elements[0]) == 4 and len(date_elements[1]) == 2 and len(date_elements[2]) == 0:
                grp.set("when", "%s-%s" % (date_elements[0], date_elements[1]))
            if len(date_elements[0]) == 4 and len(date_elements[1]) == 0 and len(date_elements[2]) == 0:
                grp.set("when", date_elements[0])
    return div


def generate_tei_document(header: FileStorage, pages: List[FileStorage], config: dict = None) -> Element:
    """
    Generate a TEI document from header and pages

    :param header: FileStorage of header
    :param pages: list of FileStorage
    :param config: configuration dictionary
        {
            'NameTag': str[],   # Default ["a", "g", "i", "m", "n", "o", "p", "t"]
            'UDPipe': str[],    # Default ["n", "lemma", "pos", "msd", "join"]
            'ALTO': str[]       # Default ["width", "height", "vpos", "hpos"]
        }
    :returns: an XML document
    """
    # Prepare config with default values
    default_config = {
        "NameTag": ["a", "g", "i", "m", "n", "o", "p", "t"],
        "UDPipe": ["n", "lemma", "pos", "msd", "join"],
        "ALTO": ["width", "height", "vpos", "hpos"]
    }
    if config is None:
        config = {}

    # If a category of filter is not in config, fill it in
    for category in default_config:
        if category not in config or config[category] is None:
            config[category] = default_config[category]

    # Create top XML document
    tei = Element("TEI", {"xmlns": "http://www.tei-c.org/ns/1.0"})

    # NameTag properties that have to be deleted
    name_tag_properties_to_remove = list(set(default_config["NameTag"]) - set(config["NameTag"]))

    # Create teiHeader
    tei_header = parse(header.stream).getroot()
    tei.append(tei_header)
    for attr in tei_header.attrib:
        tei.set(attr, tei_header.attrib.get(attr))
    tei_header.attrib.clear()

    # Remove unused NameTag elements
    for interp_group in tei_header.findall(".//interpGrp"):
        for sub in list(interp_group):
            for attr in sub.attrib:
                if attr[-2:] == "id" and sub.attrib[attr].lower()[8] in name_tag_properties_to_remove:
                    interp_group.remove(sub)

    # Prepare ALTO prefixes
    default_alto_config = ["alto-" + x for x in default_config["ALTO"]]
    alto_config = ["alto-" + x for x in config["ALTO"]]
    use_alto = len(list(set(default_alto_config) & set(alto_config))) > 0

    # Create facsimile
    facsimile = None
    if use_alto:
        facsimile = SubElement(tei, "facsimile")

    # Create text
    text = SubElement(tei, "text")
    body = SubElement(text, "body")

    # Create pages
    word_id = 1
    for page in pages:
        page_element = parse(page.stream).getroot()

        # Create a surface
        surface = None
        if use_alto and facsimile is not None:
            surface_attrs = {}
            pb = page_element.findall(".//pb")
            if pb:
                pb = pb.pop()
                for attr in pb.attrib:
                    if attr[-2:] == "id":
                        surface_attrs["start"] = "#%s" % pb.attrib[attr]
            surface = SubElement(facsimile, "surface", surface_attrs)

        # Find all words
        for word in page_element.findall(".//w") + page_element.findall(".//pc"):
            # Transform alto attributes to zones in the surface
            if use_alto and surface is not None:
                alto_attrs_in_word = list(set(word.attrib) & set(default_alto_config) & set(alto_config))
                if len(alto_attrs_in_word) > 0:
                    current_word_id = "W-"+str(word_id)
                    word.attrib["xml:id"] = current_word_id
                    zone = SubElement(surface, "zone", {"start": "#"+current_word_id})
                    if "alto-hpos" in alto_attrs_in_word:
                        zone.attrib["ulx"] = word.attrib["alto-hpos"]
                    if "alto-vpos" in alto_attrs_in_word:
                        zone.attrib["uly"] = word.attrib["alto-vpos"]
                    if "alto-width" in alto_attrs_in_word and "alto-hpos" in word.attrib:
                        zone.attrib["lrx"] = str(float(word.attrib["alto-hpos"]) + float(word.attrib["alto-width"]))
                    if "alto-height" in alto_attrs_in_word and "alto-vpos" in word.attrib:
                        zone.attrib["lry"] = str(float(word.attrib["alto-vpos"]) + float(word.attrib["alto-height"]))
                    word_id += 1
            for attr in default_alto_config:
                if attr in word.attrib:
                    word.attrib.pop(attr)

            # For all possible UDPipe attributes
            for prop in default_config["UDPipe"]:
                # If is not in config, remove it from the word
                if prop not in config["UDPipe"] and prop in word.attrib:
                    word.attrib.pop(prop)

        # Find all NameTag elements and remove them
        recursive_remove_name_tag(page_element, name_tag_properties_to_remove)

        body.append(page_element)
    return tei


def recursive_remove_name_tag(element: Element, properties: List[str]):
    i = 0
    for sub in list(element):
        recursive_remove_name_tag(sub, properties)
        if 'ana' in sub.attrib:
            ana_prop = sub.attrib.get('ana').lower()
            if ana_prop.startswith('#nametag-') and ana_prop[9] in properties:
                for sub_sub in list(sub):
                    element.insert(i, sub_sub)
                    i += 1
                element.remove(sub)
                i -= 1
        i += 1
