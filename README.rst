ApiSports
---------


.. image:: https://img.shields.io/github/license/MikeSmithEU/apisports.svg
    :target: https://github.com/MikeSmithEU/apisports/blob/main/LICENSE

.. image:: https://img.shields.io/github/workflow/status/MikeSmithEU/apisports/Python%20package
    :alt: GitHub Workflow Status (branch)
    :target: https://github.com/MikeSmithEU/apisports/actions

.. image:: https://readthedocs.org/projects/apisports/badge/?version=latest
    :target: https://apisports.readthedocs.io/
    :alt: Documentation Status

A simple python library for easy querying of APISports data.

Example usage
=============

.. code-block:: python3

    from apisports import Football

    api = Football(api_key='XXXXXXXX')

    # get all players for Chelsea FC (id=49) for the 2020 season
    # and sort by age

    players = api.players(season=2020, team=49)

    if not players.ok:
        print("something went wrong: " + players.error_description())
    else:
        sorted_by_age = sorted(players, key=lambda player : player['player']['age'])
        def format_player(player):
            return "{firstname} {lastname}: {age}".format(
                firstname = player['player']['firstname'],
                lastname = player['player']['lastname'],
                age = player['player']['age']
            )

        for player in sorted_by_age:
            print(format_player(player))

outputs::

    Harvey Vale: 18
    Dynel Simeu: 19
    Myles Peart-Harris: 19
    Ian Maatsen: 19
    Valentino Livramento: 19
    Lewis Bate: 19
    Karlo Žiger: 20
    Henry Lawrence: 20
    Billy Gilmour: 20
    Faustino Anjorin: 20
    Armando Broja: 20
    Marc Guehi: 21
    Conor Gallagher: 21
    Tariq Lamptey: 21
    Juan Familia-Castillo: 21
    Ethan Ampadu: 21
    Callum Hudson-Odoi: 21
    Jamie Cumming: 22
    Luke McCormick: 22
    Kai Havertz: 22
    Mason Mount: 22
    Reece James: 22
    Christian Pulisic: 23
    Nathan Baxter: 23
    Isaiah Brown: 24
    Fikayo Tomori: 24
    Jake Clarke-Salter: 24
    Tammy Bakumo-Abraham: 24
    Ruben Loftus-Cheek: 25
    Robert Kenedy Nunes do Nascimento: 25
    Ben Chilwell: 25
    Timo Werner: 25
    Andreas Bødtker Christensen: 25
    Lewis Baker: 26
    Kepa Arrizabalaga Revuelta: 27
    Emerson Palmieri dos Santos: 27
    Mateo Kovačić: 27
    Kurt Happy Zouma: 27
    Ross Barkley: 28
    Hakim Ziyech: 28
    Antonio Rüdiger: 28
    Michy Batshuayi Tunga: 28
    Davide Zappacosta: 29
    Edouard Mendy: 29
    Jorge Luiz Frello Filho: 30
    N'Golo Kanté: 30
    Victor Moses: 31
    Marcos Alonso Mendoza: 31
    César Azpilicueta Tanco: 32
    Willian Borges da Silva: 33
    Pedro Eliezer Rodríguez Ledesma: 34
    Olivier Giroud: 35
    Thiago Emiliano da Silva: 37
    Wilfredo Daniel Caballero: 40

TODO
....

 - add unit tests