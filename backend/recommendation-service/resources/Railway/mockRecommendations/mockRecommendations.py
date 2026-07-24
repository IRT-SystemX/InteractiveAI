
import json


################################################################
######### Event 1 Recommendations ##############################
################################################################

Reco11 = json.dumps({
"data": {
                "title": "Stay at the St Pierre des Corps station",
                "description" : "Hold the train in the St Pierre des Corps station until traffic resumes.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "78",
                        "nb_impacted_passengers" : "468",
                        "total_cost" : "32838",
                        "delay" : "1h30",
                        "best": "True",
                        }
                    
        }
}
)

Reco12 = json.dumps({
"data": {
                "title": "Delay",
                "description" : "Hold the train on the track until traffic resumes. Arrangements for passenger support.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "87",
                        "nb_impacted_passengers" : "398",
                        "total_cost" : "34626",
                        "delay" : "1h30",
                        "best": "False",
                        }
                    
        }
}
)


Reco13 = json.dumps({
"data": {
                "title": "Reroute",
                "description" : "Reroute the trains. Passengers traveling to and from Poitiers are being assisted.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "102",
                        "nb_impacted_passengers" : "350",
                        "total_cost" : "35700",
                        "delay" : "1h40",
                        "best": "False",
                        }
                    
        }
}
)


Reco14 = json.dumps({
"data": {
                "title": "Cancel",
                "description" : "Train services are cancelled. Passengers are advised to postpone their journey.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "233",
                        "nb_impacted_passengers" : "468",
                        "total_cost" : "109044",
                        "delay" : "1h45",
                        "best": "False",
                        }
                    
        }
}
)

################################################################
######### Event 2 Recommendations ##############################
################################################################


Reco21 = json.dumps({
"data": {
                "title": "Stay at the station",
                "description" : "Hold the train in the Poitiers station until traffic resumes.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "123",
                        "nb_impacted_passengers" : "459",
                        "total_cost" : "56457",
                        "delay" : "1h05",
                        "best": "False",
                        }
                    
        }
}
)





Reco22 = json.dumps({
"data": {
                "title": "Delay",
                "description" : "Hold the train on the track until traffic resumes. Arrangements for passenger support.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "129",
                        "nb_impacted_passengers" : "459",
                        "total_cost" : "59211",
                        "delay" : "1h00",
                        "best": "False",
                        }
                    
        }
}
)

Reco23 = json.dumps({
"data": {
                "title": "Reroute",
                "description" : "Diversion and rerouting of trains to the standard line between Angoulême and Poitiers. ",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "73",
                        "nb_impacted_passengers" : "459",
                        "total_cost" : "33507",
                        "delay" : "1h00",
                        "best": "True",
                        }
                    
        }
}
)


Reco24 = json.dumps({
"data": {
                "title": "Cancel",
                "description" : "Train services are cancelled. Passengers are advised to postpone their journey.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "221",
                        "nb_impacted_passengers" : "459",
                        "total_cost" : "101439",
                        "delay" : "1h00",
                        "best": "False",
                        }
                    
        }
}
)


################################################################
######### Event 3 Recommendations ##############################
################################################################

Reco31 = json.dumps({
"data": {
                "title": "Wait at the Bordeaux station",
                "description" : "Hold the train at the station until traffic resumes.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "94",
                        "nb_impacted_passengers" : "348",
                        "total_cost" : "32712",
                        "delay" : "00h30",
                        "best": "True",
                        }
                    
        }
}
)


Reco32 = json.dumps({
"data": {
                "title": "Delay",
                "description" : "Hold the train on the track until traffic resumes. Arrangements for passenger support.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "94",
                        "nb_impacted_passengers" : "347",
                        "total_cost" : "32618",
                        "delay" : "00h53",
                        "best": "False",
                        }
                    
        }
}
)


Reco33 = json.dumps({
"data": {
                "title": "Rerouting from Bordeaux to Angoulême ",
                "description" : "Diversion and rerouting of trains to the standard line between Angoulême and Poitiers.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "95",
                        "nb_impacted_passengers" : "348",
                        "total_cost" : "33060",
                        "delay" : "1h24",
                        "best": "False",
                        }
                    
        }
}
)

Reco34 = json.dumps({
"data": {
                "title": "Supprimer",
                "description" : "Train services are cancelled. Passengers are advised to postpone their journey.",
                "use_case": "Railway",
                "agent_type": "AI",
                "kpis": {
                        "cost" : "257",
                        "nb_impacted_passengers" : "348",
                        "total_cost" : "89436",
                        "delay" : "00h40",
                        "best": "False",
                        }
                    
        }
}
)


RECOMMENDATION_CATALOG = {
    "1": [Reco11, Reco12, Reco13, Reco14],
    "2": [Reco21, Reco22, Reco23, Reco24],
    "3": [Reco31, Reco32, Reco33, Reco34],
}
