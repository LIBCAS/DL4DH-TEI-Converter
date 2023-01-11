# DL4DH-TEI-Converter
DL4DH TEI Converter

TEI Converter umožňuje konvertovat a exportovat data a metadata ze systému Kramerius ve formátu TEI, který patří mezi hlavní standardy v oblasti digitálních humanitních věd pro detailní popis dokumentů v digitální podobě. Nový softwarový nástroj zajistí kompatibilitu s dalšími projekty a v případě potřeby umožní vzhledem k možnostem TEI obohacení popisu dokumentů z digitálních knihoven v systému Kramerius.

Strojové využití je popsáno níže. V praxi lze využít TEI Converter prostřednictvím webového rozhraní aplikace Kramerius plus pro konverzi/obohacení dat z digitální knihovny provozované v systému Kramerius. Více viz https://github.com/LIBCAS/DL4DH-Kramerius-plus/wiki/Webov%C3%A1-aplikace.

**Projekt „DL4DH – vývoj nástrojů pro efektivnější využití a vytěžování dat z digitálních knihoven k posílení výzkumu digital humanities“ byl podpořen Ministerstvem kultury ČR v rámci programu aplikovaného výzkumu NAKI II pod ID DG20P02OVV002 a jeho řešení probíhalo v letech 2020 – 2022.**

Na projektu spolupracují Knihovna AV ČR, v. v. i., Národní knihovna ČR, Moravská zemská knihovna v Brně a firma InQool a.s.

Koordinátorem vývoje je Knihovna AV ČR, v. v. i., zastoupená Ing. Martinem Lhotákem, lhotak@knav.cz.

Další informace a dokumentace k nástroji DL4DH TEI Converter jsou dispozici na https://github.com/LIBCAS/DL4DH-TEI-Converter/wiki.

Souhrnná informace k projektu DL4DH je umístěna na https://github.com/LIBCAS/DL4DH

# Requirements

- python 3 (tested with 3.8)
- python venv (`apt install python3.8-venv`)

# Development

## Linux (bash)

- create a virtual environment (venv): `python3 -m venv venv`
- activate the venv: `. ./venv/bin/activate`
- install requirements: `pip install -r requirements.txt`
- run the server: `export FLASK_APP=app && flask run`
- if you want to exit, terminate server app (Ctrl+C) and exit the venv: `deactivate`

## Windows (CMD)

- create a virtual environment (venv): `py -3 -m venv venv`
- activate the venv: `venv\Scripts\activate`
- install requirements: `pip install -r requirements.txt`
- run the server: 
```
set FLASK_APP=app
flask run
```
- if you want to exit, terminate server app (Ctrl+C) and exit the venv: `deactivate`

# Endpoints documentation

Swagger UI is available on `http://127.0.0.1:5000/tei/`.
Swagger documentation is available on `http://127.0.0.1:5000/tei/swagger.json`.

# Test the endpoints

### Convert Kramerius+ JSON to TEI

Generate partial TEI documents from JSON:

`curl -X POST -H "Content-Type: application/json" -d @examples/header.json http://127.0.0.1:5000/tei/convert/header/`

`curl -X POST -H "Content-Type: application/json" -d @examples/page.json http://127.0.0.1:5000/tei/convert/page/`

Save the responses from previous requests to files `examples/header.xml` and `examples/page.xml`. 
Then you can call the merge service:

`curl -X POST -F 'header=@examples/header.xml' -F 'page[]=@examples/page.xml' http://127.0.0.1:5000/tei/merge/`

`curl -X POST -F 'header=@examples/header.xml' -F 'page[]=@examples/page.xml' -F 'UDPipe=n' -F 'NameTag=p' http://127.0.0.1:5000/tei/merge/`
