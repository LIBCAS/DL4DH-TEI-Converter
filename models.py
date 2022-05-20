from werkzeug.datastructures import FileStorage


def generate_page_model(api):
    return api.schema_model('Page', {
        "type": "object",
        "required": [
            "id",
            "title",
            "tokens"
        ],
        "properties": {
            "id": {
                "type": "string",
                "description": "UUID stránky"
            },
            "title": {
                "type": "string",
                "description": "Nadpis stránky"
            },
            "source": {
                "type": "string",
                "description": "URL na zdroje stránky, napríklad https://dnnt.mzk.cz/view/uuid:57f3ff20-9ee3-11e3-8b69"
                               "-005056825209?page=uuid:ecabc240-a45d-11e3-b74a-5ef3fc9ae867 "
                               "https://dnnt.mzk.cz/search/api/v5.0/item/uuid:ecabc240-a45d-11e3-b74a-5ef3fc9ae867/"
            },
            "tokens": {
                "type": "array",
                "description": "Pole slov",
                "items": {
                    "type": "object",
                    "required": [
                        "content",
                        "linguisticMetadata"
                    ],
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Slovo v texte"
                        },
                        "nameTagMetadata": {
                            "type": "string",
                            "description": "Výstup ku danému slovu z nástroja NameTag."
                        },
                        "linguisticMetadata": {
                            "type": "object",
                            "description": "Výstup ku danému slovu z nástroja UDPipe.",
                            "required": [
                                "position",
                                "lemma"
                            ],
                            "properties": {
                                "position": {
                                    "type": "number",
                                    "description": "Pozícia slova vo vete, číslované od 1."
                                },
                                "uPosTag": {
                                    "type": "string",
                                    "description": "Výstup z nástroja UDPipe."
                                },
                                "misc": {
                                    "type": "string",
                                    "description": "Výstup z nástroja UDPipe."
                                },
                                "feats": {
                                    "type": "string",
                                    "description": "Výstup z nástroja UDPipe."
                                },
                                "lemma": {
                                    "type": "string",
                                    "description": "Slovo v základnom tvare."
                                }
                            }
                        },
                        "altoMetadata": {
                            "type": "object",
                            "description": "Informácie z formátu alto.",
                            "required": [
                                "width",
                                "height",
                                "vpos",
                                "hpos"
                            ],
                            "properties": {
                                "width": {
                                    "type": "number"
                                },
                                "height": {
                                    "type": "number"
                                },
                                "vpos": {
                                    "type": "number"
                                },
                                "hpos": {
                                    "type": "number"
                                }
                            }
                        }
                    }
                }
            }
        }
    })


def generate_header_model(api):
    return api.schema_model('Header', {
        "type": "object",
        "required": [
            "author",
            "identifiers",
            "originInfo",
            "physicalDescription",
            "title"
        ],
        "properties": {
            "title": {
                "type": "string",
                "description": "Nadpis publikácie"
            },
            "source": {
                "type": "string",
                "description": "URL na zdroje publikácie, napríklad "
                               "https://dnnt.mzk.cz/view/uuid:57f3ff20-9ee3-11e3-8b69-005056825209 "
                               "https://dnnt.mzk.cz/search/api/v5.0/item/uuid:57f3ff20-9ee3-11e3-8b69-005056825209/ "
            },
            "physicalDescription": {
                "type": "object",
                "required": [
                    "extent"
                ],
                "properties": {
                    "extent": {
                        "type": "string",
                        "description": "Fyzické rozmery publikácie"
                    }
                }
            },
            "author": {
                "type": "object",
                "required": [
                    "type",
                    "name",
                    "identifier"
                ],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["corporate", "person"],
                        "description": "Typ autora"
                    },
                    "name": {
                        "type": "string",
                        "description": "Názov/meno autora"
                    },
                    "identifier": {
                        "type": "string",
                        "description": "Identifikátor autora"
                    }
                }
            },
            "originInfo": {
                "type": "object",
                "required": [
                    "publisher",
                    "date",
                    "places"
                ],
                "properties": {
                    "publisher": {
                        "type": "string",
                        "description": "Vydávateľ"
                    },
                    "date": {
                        "type": "string",
                        "description": "Dátum vydania"
                    },
                    "places": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Miesto vydania"
                        }
                    }
                }
            },
            "identifiers": {
                "type": "array",
                "description": "Identifikátory publikácie",
                "items": {
                    "type": "object",
                    "required": [
                        "type",
                        "value"
                    ],
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Typ identifikátora"
                        },
                        "value": {
                            "type": "string",
                            "description": "Hodnota identifikátora"
                        }
                    }
                }
            },
            "processedBy": {
                "type": "array",
                "description": "Aplikácie použité pre spracovanie",
                "items": {
                    "type": "object",
                    "required": [
                        "identifier",
                        "version"
                    ],
                    "properties": {
                        "identifier": {
                            "type": "string",
                            "description": "Identifikátor nástroja/aplikácie"
                        },
                        "version": {
                            "type": "string",
                            "description": "Verzia nástroja/aplikácie"
                        },
                        "from": {
                            "type": "string",
                            "description": "Dátum použitia nástroja/aplikácie, od"
                        },
                        "to": {
                            "type": "string",
                            "description": "Dátum použitia nástroja/aplikácie, do"
                        },
                        "when": {
                            "type": "string",
                            "description": "Dátum použitia nástroja/aplikácie"
                        },
                        "label": {
                            "type": "string",
                            "description": "Bližší popis nástroja/aplikácie"
                        }
                    }
                }
            }
        }
    })


def generate_merge_parser(api):
    merge_parser = api.parser()
    merge_parser.add_argument('header', location='files', type=FileStorage, required=True,
                              help='TEI hlavička dokumentu vygenerovaná službou `POST /convert/header`')
    merge_parser.add_argument('page[]', location='files', type=FileStorage, required=True,
                              help='TEI stránok dokumentu vygenerované službou `POST /convert/page`. Môže byť '
                                   'vložených opakovane pre zlúčenie viac stránok do dokumentu')
    merge_parser.add_argument('NameTag', type=str, location='form',
                              help='Filtrácia NameTag rozpoznaných entít. Uveďte zoznam skupín entít, ktoré majú byť '
                                   'zachované. Zoznam podporovaných skupín: `a,g,i,m,n,o,p,t`')
    merge_parser.add_argument('UDPipe', type=str, location='form',
                              help='Filtrácia UDPipe rozpoznaných atribútov. Uveďte zoznam (oddelené čiarkou) '
                                   'atribútov, ktoré majú byť zachované. Zoznam podporovaných atribútov: '
                                   '`n,lemma,pos,msd,join`')
    merge_parser.add_argument('ALTO', type=str, location='form',
                              help='Filtrácia ALTO rozpoznaných atribútov. Uveďte zoznam (oddelené čiarkou) atribútov, '
                                   'ktoré majú byť zachované. Zoznam podporovaných atribútov: `width,height,vpos,hpos`')
    return merge_parser
